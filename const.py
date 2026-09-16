from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
if (user := os.environ.get("ANILIST_USER")) is None:
    raise ValueError("Username Environment Variable Not Set")
USERNAME: str = user

ANIMETHEMES_URL: str = "https://graphql.animethemes.moe"
ANILIST_URL: str = 'https://graphql.anilist.co'

ANILIST_QUERY: str = '''
query ($username: String) {
    MediaListCollection(userName: $username, type: ANIME, status: COMPLETED, sort: [SCORE_DESC]) {
        lists {
            entries {
                score(format: POINT_10_DECIMAL)
                media {
                    id
                    title {
                        english
                    }
                }
            }
        }
    }
}
'''

ANIMETHEMES_QUERY: str = '''
query ($id: [Int!]) {
  findAnimeByExternalSite(site: ANILIST, id: $id) {
    animethemes {
      animethemeentries {
        videos {
          nodes {
            filename
            link
          }
        }
      }
    }
  }
}
'''

SAVE_FILE: Path = Path("watchlist.txt")
SKIP_FILE: Path = Path("skiplist.txt")
