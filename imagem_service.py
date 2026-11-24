"""
Interface do serviço de imagens dos Pokémons.

Em Python, uma "interface" é feita com uma classe abstrata (módulo abc):
ela define O QUE deve existir, mas não COMO é feito.

O resto do sistema (telas, DAO) conhece apenas esta interface, e não a
classe que acessa a internet. Se um dia a fonte das imagens mudar,
nada mais no projeto precisa ser alterado.

IMPORTANTE: pela regra do projeto, a API é usada SOMENTE para a imagem.
Nome, tipo, altura etc. são digitados pelo usuário.
"""

from abc import ABC, abstractmethod


class ImagemPokemonError(Exception):
    """Erro próprio do serviço de imagens (mensagem amigável para a tela)."""


class ImagemPokemonService(ABC):
    """Contrato: toda classe de imagens precisa ter o método baixar_imagem."""

    @abstractmethod
    def baixar_imagem(self, numero_pokedex: int) -> bytes:
        """
        Baixa a imagem do Pokémon pelo número da Pokédex e devolve os
        bytes do PNG, prontos para gravar no banco (coluna BLOB).

        Lança ImagemPokemonError se o número for inválido ou o download falhar.
        """
        raise NotImplementedError
