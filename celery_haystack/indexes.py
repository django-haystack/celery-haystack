from haystack import indexes


class CelerySearchIndex(indexes.SearchIndex):
    task_path = None
