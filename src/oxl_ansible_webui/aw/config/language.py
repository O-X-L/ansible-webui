from aw.config.languages.en import EN
from aw.config.languages.de import DE

LANGUAGES = [
    ('en', 'English'),
    ('de', 'Deutsch'),
]

# NOTE: the client will use the english translation if another lang has missing codes
TRANSLATIONS = {
    'en': EN,
    'de': DE,
}
