from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db.models.loading import get_model

from .conf import settings

try:
    from haystack import connections, connection_router
    from haystack.exceptions import NotHandled as IndexNotFoundException
    legacy = False
except ImportError:
    try:
        from haystack import site
        from haystack.exceptions import NotRegistered as IndexNotFoundException  # noqa
        legacy = True
    except ImportError as e:
        raise ImproperlyConfigured("Haystack couldn't be imported: %s" % e)

if settings.CELERY_HAYSTACK_TRANSACTION_SAFE and not getattr(settings, 'CELERY_ALWAYS_EAGER', False):
    from djcelery_transactions import PostTransactionTask as Task
else:
    from celery.task import Task  # noqa

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


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
            raise ImproperlyConfigured("Could not load model '%s'." %
                                       object_path)
        return model_class

    def get_instance(self, model_class, pk, **kwargs):
        """
        Fetch the instance in a standarized way.
        """
        instance = None
        try:
            instance = model_class._default_manager.get(pk=pk)
        except model_class.DoesNotExist:
            logger.error("Couldn't load %s.%s.%s. Somehow it went missing?" %
                         (model_class._meta.app_label.lower(),
                          model_class._meta.object_name.lower(), pk))
        except model_class.MultipleObjectsReturned:
            logger.error("More than one object with pk %s. Oops?" % pk)
        return instance

    def get_indexes(self, model_class, **kwargs):
        """
        Fetch the model's registered ``SearchIndex`` in a standarized way.
        """
        try:
            if legacy:
                index_holder = site
                yield index_holder.get_index(model_class), self.using
            else:
                using_backends = connection_router.for_write(**{'models': [model_class]})
                for using in using_backends:
                    index_holder = connections[using].get_unified_index()
                    yield index_holder.get_index(model_class), using
        except IndexNotFoundException:
            raise ImproperlyConfigured("Couldn't find a SearchIndex for %s." %
                                       model_class)

    def run(self, action, identifier, **kwargs):
        """
        Trigger the actual index handler depending on the
        given action ('update' or 'delete').
        """
        # First get the object path and pk (e.g. ('notes.note', 23))
        object_path, pk = self.split_identifier(identifier, **kwargs)
        if object_path is None or pk is None:
            msg = "Couldn't handle object with identifier %s" % identifier
            logger.error(msg)
            raise ValueError(msg)

        # Then get the model class for the object path
        model_class = self.get_model_class(object_path, **kwargs)
        for current_index, using in self.get_indexes(model_class, **kwargs):
            current_index_name = ".".join([current_index.__class__.__module__,
                                           current_index.__class__.__name__])

            if action == 'delete':
                # If the object is gone, we'll use just the identifier
                # against the index.
                try:
                    current_index.remove_object(identifier, using=using)
                except Exception as exc:
                    logger.exception(exc)
                    self.retry(exc=exc)
                else:
                    msg = ("Deleted '%s' (with %s)" %
                           (identifier, current_index_name))
                    logger.debug(msg)
            elif action == 'update':
                # and the instance of the model class with the pk
                instance = self.get_instance(model_class, pk, **kwargs)
                if instance is None:
                    logger.debug("Failed updating '%s' (with %s)" %
                                 (identifier, current_index_name))
                    raise ValueError("Couldn't load object '%s'" % identifier)

                # Call the appropriate handler of the current index and
                # handle exception if neccessary
                try:
                    current_index.update_object(instance, using=using)
                except Exception as exc:
                    logger.exception(exc)
                    self.retry(exc=exc)
                else:
                    msg = ("Updated '%s' (with %s)" %
                           (identifier, current_index_name))
                    logger.debug(msg)
            else:
                logger.error("Unrecognized action '%s'. Moving on..." % action)
                raise ValueError("Unrecognized action %s" % action)


class CeleryHaystackUpdateIndex(Task):
    """
    A celery task class to be used to call the update_index management
    command from Celery.
    """
    def run(self, apps=None, **kwargs):
        defaults = {
            'batchsize': settings.CELERY_HAYSTACK_COMMAND_BATCH_SIZE,
            'age': settings.CELERY_HAYSTACK_COMMAND_AGE,
            'remove': settings.CELERY_HAYSTACK_COMMAND_REMOVE,
            'using': [settings.CELERY_HAYSTACK_DEFAULT_ALIAS],
            'workers': settings.CELERY_HAYSTACK_COMMAND_WORKERS,
            'verbosity': settings.CELERY_HAYSTACK_COMMAND_VERBOSITY,
        }
        defaults.update(kwargs)
        if apps is None:
            apps = settings.CELERY_HAYSTACK_COMMAND_APPS
        # Run the update_index management command
        logger.info("Starting update index")
        call_command('update_index', *apps, **defaults)
        logger.info("Finishing update index")
