import urllib.error
import urllib.request

from api.imagem_service import ImagemPokemonError, ImagemPokemonService


class PokeApiImagemService(ImagemPokemonService):

    _URL_ARTE_OFICIAL = (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        "sprites/pokemon/other/official-artwork/{}.png"
    )
    _URL_SPRITE = (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
        "sprites/pokemon/{}.png"
    )
    _NUMERO_MAXIMO = 1025  

    def __init__(self, timeout: int = 15):
        self._timeout = timeout

    def baixar_imagem(self, numero_pokedex: int) -> bytes:
        self._validar_numero(numero_pokedex)

        for modelo in (self._URL_ARTE_OFICIAL, self._URL_SPRITE):
            imagem = self._tentar_baixar(modelo.format(numero_pokedex))
            if imagem:
                return imagem

        raise ImagemPokemonError(
            f"Imagem não encontrada para o Pokémon nº {numero_pokedex}."
        )


    def _validar_numero(self, numero) -> None:
        if not isinstance(numero, int) or not 1 <= numero <= self._NUMERO_MAXIMO:
            raise ImagemPokemonError(
                f"Número inválido: {numero}. Use um valor entre 1 e {self._NUMERO_MAXIMO}."
            )

    def _tentar_baixar(self, url: str):
        requisicao = urllib.request.Request(url, headers={"User-Agent": "Pokedex-Etec"})
        try:
            with urllib.request.urlopen(requisicao, timeout=self._timeout) as resposta:
                dados = resposta.read()
                return dados or None
        except urllib.error.HTTPError:
            return None  
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise ImagemPokemonError(
                "Sem conexão com a internet ou servidor indisponível."
            ) from e
