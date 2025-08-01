"""
Music analysis related exceptions
"""
from . import TempoCraftError

class AnalysisError(TempoCraftError):
    """Base analysis error"""
    pass

class BPMAnalysisError(AnalysisError):
    """Failed to analyze BPM"""
    pass

class GenreAnalysisError(AnalysisError):
    """Failed to analyze genres"""
    pass

class AudioFeaturesError(AnalysisError):
    """Failed to get audio features"""
    pass

class ExternalAPIError(AnalysisError):
    """External API service error"""
    pass

class DataNotFoundError(AnalysisError):
    """Requested data not found"""
    pass
