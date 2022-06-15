import json
import time
import pickle
import gspread

from gspread import Worksheet
from django.conf import settings
from instagrapi.types import Hashtag
from instagrapi import Client as InstaClient


class Client:
    def __init__(self, number=0):
        self.sheet_number = number
        self.gc = None
        self.sheet: Worksheet = None
        self.data = None
        self.file = None

    def set_oauth(self):
        self.gc = gspread.oauth(
            credentials_filename=str(settings.SHEETS_CREDENTIALS_FILEPATH),
            authorized_user_filename=str(settings.SHEETS_AUTHORIZATION_FILEPATH)
        )

    def set_file(self):
        self.file = self.gc.open('psychology-hashtags')

    def set_sheet(self):
        self.sheet = self.file.get_worksheet(self.sheet_number)

    def eval(self):
        self.data: list[list[str]] = self.sheet.get_all_values()

    def setup(self):
        self.set_oauth()
        self.set_file()
        self.set_sheet()
        self.eval()

    def get_cell(self, address: str) -> str:
        row = int(address[1:]) - 1
        col = ord(address[0].upper()) - 65
        return self.data[row][col]

    def get_col_cells(self, col: str) -> list[str]:
        col = ord(col.upper()) - 65
        return [self.data[row][col] for row in range(len(self.data))]

    def get_row_cells(self, row: int) -> list[str]:
        return self.data[row]

    def picklify(self):
        folder = settings.BASE_DIR / 'data'
        folder.mkdir(exist_ok=True)
        with open(folder / 'sheet.pickle', 'wb') as file:
            pickle.dump((self.gc, self.sheet, self.data), file)

    def unpicklify(self):
        folder = settings.BASE_DIR / 'data'
        folder.mkdir(exist_ok=True)
        with open(folder / 'sheet.pickle', 'rb') as file:
            self.gc, self.sheet, self.data = pickle.load(file)

    def update_tags(self, tags: list[Hashtag], starting_row: int):
        tags.sort(key=lambda x: x.media_count)
        self.sheet.update(f'B{starting_row}:D{starting_row - 1 + len(tags)}',
                          [[tag.name, tag.media_count] for tag in tags])

    def search_hashtags(self, query: str, client: InstaClient, all_tags: list[Hashtag]):
        from observations.scripts.client import search_hashtags
        tags = search_hashtags(client, query, 100)
        tags = [tag for tag in tags if tag not in all_tags]
        all_tags.extend(tags)
        return tags

    def search_and_update_tags(self, queries: list[str], client: InstaClient = None, all_tags: list[Hashtag] = None,
                               data: list = None):
        from observations.scripts.client import setup_client
        client = setup_client() if client is None else client
        all_tags = list() if all_tags is None else all_tags
        data = list() if data is None else data
        for query in queries:
            time.sleep(10)
            tags = self.search_hashtags(query, client, all_tags)
            print(f'done query={query}')
            tags.sort(key=lambda x: x.media_count)
            data.append([query, '', ''])
            for tag in tags:
                data.append(['', tag.name, tag.media_count])
            data.append(['', '', ''])

        with open('/tmp/data.json', 'w') as file:
            json.dump(data, file)
        with open('/tmp/all_tags.json', 'w') as file:
            json.dump(list(map(lambda x: x.dict(), all_tags)), file)
        print('took_backup!')
        print(self.sheet.update(f'A1:C{len(data)}', data, raw=False))
        print('sheet updated!')

    def define_named_range(self, name: str, starting_row: int, ending_row: int):
        self.sheet.define_named_range(f"C{starting_row}:C{ending_row}", f"{self.sheet.title}_{name}")

    def calculate_strength(self, name: str, starting_row: int, ending_row: int):
        self.define_named_range(name, starting_row, ending_row)
        data = list()
        for row in range(starting_row, ending_row + 1):
            data.append([f'=C{row} / MAX({self.sheet.title}_{name})'])
        self.sheet.update(f'D{starting_row}:D{ending_row}', data, raw=False)
