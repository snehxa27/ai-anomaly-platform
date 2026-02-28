class TrainingError(Exception):
    pass


class DataLoadError(TrainingError):
    pass


class DataValidationError(TrainingError):
    pass


class ArtifactSaveError(TrainingError):
    pass

