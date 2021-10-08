import pytest

from toxic.features.chain.chain import MarkovChain


@pytest.mark.parametrize(
    ['source', 'input', 'result'],
    [
        ([1, 2, 3], [1, 2], 3),
    ]
)
def test_markov_chain(source, input, result):
    chain = MarkovChain(window=2)
    for el in source:
        chain.teach(el)

    current = chain.get_start(input)

    assert chain.predict(current) == result
