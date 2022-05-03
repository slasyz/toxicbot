import csv
import json
import os
import random

from ruwordnet import RuWordNet
from pymorphy2 import MorphAnalyzer

from toxic.features.chain.splitters import Splitter, SpaceAdjoinSplitter


class Russian:
    def __init__(self, wn: RuWordNet, morph: MorphAnalyzer):
        self.wn = wn
        self.morph = morph

    def get_hypernyms(self, synset_ids: set[str]) -> set[str]:
        res = set()
        for synset_id in synset_ids:
            synset = self.wn[synset_id]
            for hp in synset.hypernyms:
                res.add(hp.id)

        return res

    def get_hyponyms(self, synset_ids: set[str]) -> set[str]:
        res = set()
        for synset_id in synset_ids:
            synset = self.wn[synset_id]
            for hp in synset.hyponyms:
                res.add(hp.id)

        return res

    def get_word_synsets(self, word: str, max_len: int = 2) -> set[str]:
        senses = self.wn.get_senses(word)
        return {x.synset_id for x in senses[:max(max_len, len(senses))]}

    def get_normal_forms(self, word: str, max_len: int = 2):
        parsed = self.morph.parse(word)
        return [x.normal_form for x in parsed[:max(max_len, len(parsed))]]


class Emojifier:
    def __init__(self, splitter: Splitter, russian: Russian, synsets_to_emojis: dict[str, list[str]]):
        self.splitter = splitter
        self.russian = russian
        self.synsets_to_emojis = synsets_to_emojis

    @staticmethod
    def new(splitter: Splitter, russian: Russian, csv_path: str):
        synsets_to_emojis = {}

        with open(csv_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            next(reader, None)
            for row in reader:
                _, synset, _, emojis = row
                emojis = json.loads(emojis)
                synsets_to_emojis[synset] = emojis

        return Emojifier(splitter, russian, synsets_to_emojis)

    def get_word_emojis(self, word: str) -> list[str]:
        synsets = self.russian.get_word_synsets(word)
        for synset in synsets:
            emojis = self.synsets_to_emojis.get(synset)
            if emojis is not None:
                return emojis

        hypernyms = self.russian.get_hypernyms(synsets)
        for synset in hypernyms:
            emojis = self.synsets_to_emojis.get(synset)
            if emojis is not None:
                return emojis

        hypernyms = self.russian.get_hypernyms(synsets)
        for synset in hypernyms:
            emojis = self.synsets_to_emojis.get(synset)
            if emojis is not None:
                return emojis

        return []

    def get_token_emojis(self, token: str, broad: bool, anything: bool) -> list[str]:
        normal_forms = self.russian.get_normal_forms(token)
        for word in normal_forms:
            emojis = self.get_word_emojis(word)
            if len(emojis) > 0:
                return emojis

        if broad:
            for word in normal_forms:
                synsets = self.russian.get_word_synsets(word, 2)
                if len(synsets) == 0:
                    continue

                synsets |= self.russian.get_hypernyms(synsets)
                synsets |= self.russian.get_hyponyms(synsets)

                for synset in synsets:
                    emojis = self.synsets_to_emojis.get(synset)
                    if emojis is not None:
                        return emojis

        if anything:
            emojis = random.choice(list(self.synsets_to_emojis.values()))
            return emojis

        return []

    def generate(self, text: str) -> str:
        res = []

        tokens = self.splitter.split(text)
        words_without_emoji = 0
        for token in tokens:
            broad = words_without_emoji >= 3
            anything = words_without_emoji >= 4
            emojis = self.get_token_emojis(token, broad, anything)

            if len(emojis) == 0:
                words_without_emoji += 1
                res.append(token)
                continue

            emoji = random.choice(emojis)
            words_without_emoji = 0
            res.append(token + emoji)

        return self.splitter.join(res)


def __main__():
    splitter = SpaceAdjoinSplitter()
    wn = RuWordNet()
    morph = MorphAnalyzer()
    russian = Russian(wn, morph)
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'emoji_df_result.csv')

    emojifier = Emojifier.new(splitter, russian, csv_path)

    texts = []

    for text in texts:
        res = emojifier.generate(text)
        print()
        print(res)


if __name__ == '__main__':
    __main__()
