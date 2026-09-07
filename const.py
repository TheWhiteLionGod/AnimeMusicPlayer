from dotenv import load_dotenv
import os

load_dotenv()
if (user := os.environ.get("username")) is None:
    raise ValueError("Username Environment Variable Not Set")
USERNAME: str = user

ANIMETHEMES_URL: str = "https://api.animethemes.moe/search"
ANILIST_URL: str = 'https://graphql.anilist.co'

QUERY: str = '''
query ($username: String) {
    MediaListCollection(userName: $username, type: ANIME, status: COMPLETED, sort: [SCORE_DESC]) {
        lists {
            entries {
                score(format: POINT_10_DECIMAL)
                media {
                    id
                    idMal
                    title {
                        english
                    }
                }
            }
        }
    }
}
'''
