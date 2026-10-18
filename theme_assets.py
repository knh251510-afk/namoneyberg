"""Local paired assets: time-of-day variants share a composition."""
from pathlib import Path
ROOT=Path(__file__).parent/'static'
def image_path(name,mode='light'):
    if name not in {'home-reading','home-data','home-connections','home-corporate','home-calendar','brief-macro','brief-global','brief-industry'}:raise ValueError('Unknown artwork')
    if mode not in ('light','dark'):raise ValueError('Unknown theme')
    paired=ROOT/f'{name}-{mode}.jpg'
    if paired.exists():return paired
    return ROOT/(name+('.jpg' if name.startswith('home-') else '.png'))
