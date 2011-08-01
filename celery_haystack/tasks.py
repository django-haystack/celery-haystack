from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management import call_command
from django.db.models.loading import get_model

from celery.task import Task

from haystack import connections
from haystack.exceptions import NotHandled

from celery_haystack import conf


class CeleryHaystackSignalHandler(Task):
    max_retries = conf.MAX_RETRIES
    default_retry_delay = conf.RETRY_DELAY
    using = conf.DEFAULT_ALIAS

    def split_identifier(self, identifier, **kwargs):
        """
        Break down the identifier representing the instance.

        Converts 'notes.note.23' into ('notes.note', 23).
        """
        bits = identifier.split('.')

        if len(bits) < 2:
            logger = self.get_logger(**kwargs)
            logger.error("Unable to parse object "
                         "identifer '%s'. Moving on..." % identifier)
            return (None, None)

        pk = bits[-1]
        # In case Django ever handles full paths...
        object_path = '.'.join(bits[:-1])
        return (object_path, pk)

    def get_model_class(self, object_path, **kwargs):
        """
        Fetch the model's class in a standarized way.
        """
        bits = object_path.split('.')
        app_name = '.'.join(bits[:-1])
        classname = bits[-1]
        model_class = get_model(app_name, classname)

        if model_class is None:
            logger = self.get_logger(**kwargs)
            logger.error("Could not load model "
                         "from '%s'. Moving on..." % object_path)
            return None

        return model_class

    def get_instance(self, model_class, pk, **kwargs):
        """
        Fetch the instance in a standarized way.
        """
        logger = self.get_logger(**kwargs)
        try:
            instance = model_class.objects.get(pk=int(pk))
        except ObjectDoesNotExist:
            logger.error("Couldn't load model instance "
                         "with pk #%s. Somehow it went missing? %s" % pk)
            return None
        except MultipleObjectsReturned:
            logger.error("More than one object with pk #%s. Oops?" % pk)
            return None

        return instance

    def get_index(self, model_class, **kwargs):
        """
        Fetch the model's registered ``SearchIndex`` in a standarized way.
        """
        logger = self.get_logger(**kwargs)
        try:
            connection = connections['default']
            return connection.get_unified_index().get_index(model_class)
        except NotHandled:
            logger.error("Couldn't find a SearchIndex for %s." % model_class)
            return None

    def run(self, action, identifier, **kwargs):
        """
        Trigger the actual index handler depending on the
        given action ('update' or 'delete').
        """
        logger = self.get_logger(**kwargs)

        # First get the object path and pk (e.g. ('notes.note', 23))
        object_path, pk = self.split_identifier(identifier, **kwargs)
        if object_path is None or pk is None:
            logger.error("Skipping.")
            return

        # Then get the model class for the object path
        model_class = self.get_model_class(object_path, **kwargs)
        # and the instance of the model class with the pk
        instance = self.get_instance(model_class, pk, **kwargs)
        if instance is None:
            logger.debug("Didn't update index for '%s'" % identifier)

        # Call the appropriate handler of the current index and
        # handle exception if neccessary
        logger.debug("Indexing '%s'." % instance)
        try:
            current_index = self.get_index(model_class, **kwargs)
            handlers = {
                'update': current_index.update_object,
                'delete': current_index.remove_object,
            }
            handlers[action](instance, using=self.using)
        except KeyError, exc:
            logger.error("Unrecognized action '%s'. Moving on..." % action)
            self.retry([action, identifier], kwargs, exc=exc)
        except Exception, exc:
            logger.error(exc)
            self.retry([action, identifier], kwargs, exc=exc)
        else:
            logger.debug("Updated index with '%s'" % instance)


class CeleryHaystackUpdateIndex(Task):
    """
    A celery task class to be used to call the update_index management
    command from Celery.
    """
    def run(self, apps=None, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Starting update index")
        # Run the update_index management command
        defaults = {
            'batchsize': conf.COMMAND_BATCH_SIZE,
            'age': conf.COMMAND_AGE,
            'remove': conf.COMMAND_REMOVE,
            'using': conf.DEFAULT_ALIAS,
            'workers': int(conf.COMMAND_WORKERS),
            'verbosity': int(conf.COMMAND_VERBOSITY),
        }
        defaults.update(kwargs)
        if apps is None:
            apps = conf.COMMAND_APPS
        call_command('update_index', *apps, **defaults)
        logger.info("Finishing update index")
