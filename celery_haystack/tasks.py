from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db.models.loading import get_model

from celery.task import Task
from celery_haystack.conf import settings

try:
    from haystack import connections
    index_holder = connections['default'].get_unified_index()
    from haystack.exceptions import NotHandled as IndexNotFoundException
    legacy = False
except ImportError:
    try:
        from haystack import site as index_holder
        from haystack.exceptions import NotRegistered as IndexNotFoundException
        legacy = True
    except ImportError, e:
        raise ImproperlyConfigured("Haystack couldn't be imported: %s" % e)


class CeleryHaystackSignalHandler(Task):
    using = settings.CELERY_HAYSTACK_DEFAULT_ALIAS
    max_retries = settings.CELERY_HAYSTACK_MAX_RETRIES
    default_retry_delay = settings.CELERY_HAYSTACK_RETRY_DELAY

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
        except model_class.DoesNotExist:
            logger.error("Couldn't load model instance "
                         "with pk #%s. Somehow it went missing?" % pk)
            return None
        except model_class.MultipleObjectsReturned:
            logger.error("More than one object with pk #%s. Oops?" % pk)
            return None

        return instance

    def get_index(self, model_class, **kwargs):
        """
        Fetch the model's registered ``SearchIndex`` in a standarized way.
        """
        logger = self.get_logger(**kwargs)
        try:
            return index_holder.get_index(model_class)
        except IndexNotFoundException:
            logger.error("Couldn't find a SearchIndex for %s." % model_class)
        return None

    def get_handler_options(self, **kwargs):
        options = {}
        if legacy:
            options['using'] = self.using
        return options

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
        current_index = self.get_index(model_class, **kwargs)

        if action == 'delete':
            # If the object is gone, we'll use just the identifier against the
            # index.
            try:
                handler_options = self.get_handler_options(**kwargs)
                current_index.remove_object(identifier, **handler_options)
            except Exception, exc:
                logger.error(exc)
                self.retry([action, identifier], kwargs, exc=exc)
            else:
                logger.debug("Deleted '%s' from index" % identifier)
            return

        elif action == 'update':
            # and the instance of the model class with the pk
            instance = self.get_instance(model_class, pk, **kwargs)
            if instance is None:
                logger.debug("Didn't update index for '%s'" % identifier)
                return

            # Call the appropriate handler of the current index and
            # handle exception if neccessary
            logger.debug("Indexing '%s'." % instance)
            try:
                handler_options = self.get_handler_options(**kwargs)
                current_index.update_object(instance, **handler_options)
            except Exception, exc:
                logger.error(exc)
                self.retry([action, identifier], kwargs, exc=exc)
            else:
                logger.debug("Updated index with '%s'" % instance)
        else:
            logger.error("Unrecognized action '%s'. Moving on..." % action)
            self.retry([action, identifier], kwargs, exc=exc)


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
            'batchsize': settings.CELERY_HAYSTACK_COMMAND_BATCH_SIZE,
            'age': settings.CELERY_HAYSTACK_COMMAND_AGE,
            'remove': settings.CELERY_HAYSTACK_COMMAND_REMOVE,
            'using': settings.CELERY_HAYSTACK_DEFAULT_ALIAS,
            'workers': settings.CELERY_HAYSTACK_COMMAND_WORKERS,
            'verbosity': settings.CELERY_HAYSTACK_COMMAND_VERBOSITY,
        }
        defaults.update(kwargs)
        if apps is None:
            apps = settings.CELERY_HAYSTACK_COMMAND_APPS
        call_command('update_index', *apps, **defaults)
        logger.info("Finishing update index")
