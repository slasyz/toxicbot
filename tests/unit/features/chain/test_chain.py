import pytest

from toxic.modules.neural.chains.chain import MarkovChain


@pytest.mark.parametrize(
    ['source', 'input', 'result'],
    [
        ([1, 2, 3], [1, 2], 3),
    ]
)
def test_markov_chain(source: list[int], input: list[int], result: int):
    chain = MarkovChain(window=2)
    for el in source:
        chain.teach(el)

    current = chain.get_start(input)

    assert chain.predict(current) == result
