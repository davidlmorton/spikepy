
from spikepy.common import program_text as pt

stages = ['detection_filter', 'detection', 'extraction_filter', 
        'extraction', 'clustering']

def get_stage_display_name(stage):
    return getattr(pt, stage.upper())
