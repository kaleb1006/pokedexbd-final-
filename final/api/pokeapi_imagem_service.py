"""
Implementação da interface ImagemPokemonService usando a PokeAPI.

As imagens ficam no repositório oficial de sprites da PokeAPI:
  - arte oficial (grande):  .../sprites/pokemon/other/official-artwork/{numero}.png
  - sprite simples (reserva): .../sprites/pokemon/{numero}.png

Como a URL é montada direto pelo número, NÃO lemos nenhum dado do
Pokémon na API (atende a regra "não pegar informações da API").

Usa apenas a biblioteca padrão (urllib) — não precisa instalar nada.
"""

import urllib.error
import urllib.request

from api.imagem_service import ImagemPokemonError, ImagemPokemonService


class PokeApiImagemService(ImagemPokemonService):

    # Atributos "privados" (convenção do Python: começam com _)
    _URL_ARTE_OFICIAL = (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        "sprites/pokemon/other/official-artwork/{}.png"
    )
    _URL_SPRITE = (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        "sprites/pokemon/{}.png"
    )
    _NUMERO_MAXIMO = 1025  # maior número da Pokédex nacional (geração 9)

    def __init__(self, timeout: int = 15):
        self._timeout = timeout

    def baixar_imagem(self, numero_pokedex: int) -> bytes:
        self._validar_numero(numero_pokedex)

        # 1ª tentativa: arte oficial; 2ª tentativa: sprite simples
        for modelo in (self._URL_ARTE_OFICIAL, self._URL_SPRITE):
            imagem = self._tentar_baixar(modelo.format(numero_pokedex))
            if imagem:
                return imagem

        raise ImagemPokemonError(
            f"Imagem não encontrada para o Pokémon nº {numero_pokedex}."
        )

    # ---------- métodos auxiliares (encapsulados) ----------

    def _validar_numero(self, numero) -> None:
        """Regra de negócio: só aceita números que existem na Pokédex."""
        if not isinstance(numero, int) or not 1 <= numero <= self._NUMERO_MAXIMO:
            raise ImagemPokemonError(
                f"Número inválido: {numero}. Use um valor entre 1 e {self._NUMERO_MAXIMO}."
            )

    def _tentar_baixar(self, url: str):
        """Faz o GET e devolve os bytes, ou None se a imagem não existir (404)."""
        requisicao = urllib.request.Request(url, headers={"User-Agent": "Pokedex-Etec"})
        try:
            with urllib.request.urlopen(requisicao, timeout=self._timeout) as resposta:
                dados = resposta.read()
                return dados or None
        except urllib.error.HTTPError:
            return None  # 404 ou outro erro do servidor → tenta a próxima URL
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise ImagemPokemonError(
                "Sem conexão com a internet ou servidor indisponível."
            ) from e
