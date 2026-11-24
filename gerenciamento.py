
import sqlite3

import streamlit as st

from api.imagem_service import ImagemPokemonError
from api.pokeapi_imagem_service import PokeApiImagemService
from classes.pokemon import Pokemon
from repositorio.repositorio import PokemonRepositorySQLite

st.set_page_config(
    page_title="Seu PC",
    layout="wide"
)

repositorio = PokemonRepositorySQLite()
servico_imagem = PokeApiImagemService()

st.markdown("""
<style>

.stApp {
    background-color: #172E49;
}

header[data-testid="stHeader"] {
    background-color: #172E49;
}

h1, h2, h3 {
    color: #D5EAF5;
}

p, label {
    color: #E6F2F8;
}

div[data-testid="stSidebar"] {
    background-color: #203D5D;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #294A6A;
    border: 1px solid #7097B4;
    border-radius: 12px;
    padding: 10px;
}

div.stButton > button {
    background-color: #397EA8;
    color: white;
    border-radius: 8px;
    border: 1px solid #8ABBD8;
}

div.stButton > button:hover {
    background-color: #579BC2;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ---------- estado da sessão ----------
if "pokemon_selecionado" not in st.session_state:
    st.session_state["pokemon_selecionado"] = None

# None = ainda não pesquisou | [] = pesquisou e não achou
if "resultados" not in st.session_state:
    st.session_state["resultados"] = None

if "cad_imagem" not in st.session_state:
    st.session_state["cad_imagem"] = None

if "cad_imagem_numero" not in st.session_state:
    st.session_state["cad_imagem_numero"] = None


# ---------- funções de exibição ----------
def mostrar_imagem(imagem, largura=150):
    if imagem:
        st.image(bytes(imagem), width=largura)
    else:
        st.write("Imagem não disponível")


def mostrar_dados(pokemon):
    st.subheader(pokemon.nome)

    mostrar_imagem(pokemon.imagem)

    st.write("Número:", pokemon.numero_pokedex)
    st.write("Tipo 1:", pokemon.tipo_um)
    st.write("Tipo 2:", pokemon.tipo_dois or "Não possui")

    st.write("Altura:", pokemon.altura)
    st.write("Peso:", pokemon.peso)

    st.write("Descrição:", pokemon.descricao)

    st.write("Evolução anterior:", pokemon.evolucao_antes or "Não possui")
    st.write("Próxima evolução:", pokemon.evolucao_depois or "Não possui")


def para_float(texto):
    """Converte texto em float aceitando vírgula. Vazio vira None."""
    texto = texto.strip().replace(",", ".")
    return float(texto) if texto else None


# ---------- cabeçalho e menu ----------
st.title("pc do usuario")

st.markdown(
    "<p style='text-align:center;'>POKÉMON STORAGE SYSTEM</p>",
    unsafe_allow_html=True
)

st.divider()

pagina = st.sidebar.radio(
    "MENU PRINCIPAL",
    [
        "PC Storage",
        "Pokémon Data",
        "Cadastro",
        "Management"
    ]
)

# pega info do banco de dados
todos_pokemons = repositorio.listar_todos()


# =====================================================
# PC STORAGE: mostra os pokemons já registrados
# =====================================================
if pagina == "PC Storage":

    st.header("Pokémon Storage")
    st.write("Organização dos Pokémon cadastrados.")

    total_caixas = max(1, (len(todos_pokemons) + 29) // 30)

    caixa = st.selectbox(
        "Selecionar caixa",
        range(1, total_caixas + 1),
        format_func=lambda x: f"BOX {x:02}"
    )

    inicio = (caixa - 1) * 30
    pokemons_caixa = todos_pokemons[inicio:inicio + 30]

    col_box, col_info = st.columns([2, 1])

    with col_box:

        st.subheader(f"BOX {caixa:02}")

        colunas = st.columns(6)

        for i in range(30):

            with colunas[i % 6]:

                with st.container(border=True):

                    if i < len(pokemons_caixa):

                        pokemon = pokemons_caixa[i]

                        mostrar_imagem(pokemon.imagem, 65)

                        if st.button(pokemon.nome, key=f"box_{pokemon.id}"):
                            st.session_state["pokemon_selecionado"] = pokemon.id
                            st.rerun()

                    else:
                        st.markdown(
                            "<div style='text-align:center;padding:15px;'>＋</div>",
                            unsafe_allow_html=True
                        )

    with col_info:

        st.subheader("Pokémon selecionado")

        id_selecionado = st.session_state["pokemon_selecionado"]

        if id_selecionado:

            pokemon = repositorio.buscar_id(id_selecionado)

            if pokemon:
                mostrar_dados(pokemon)
            else:
                st.info("Pokémon não encontrado.")

        else:
            st.info("Selecione um Pokémon na caixa.")


# =====================================================
# POKÉMON DATA: mostra os dados do pokemon selecionado
# =====================================================
elif pagina == "Pokémon Data":

    st.header("Pokémon Data")

    id_selecionado = st.session_state["pokemon_selecionado"]

    if id_selecionado:

        pokemon = repositorio.buscar_id(id_selecionado)

        if pokemon:
            mostrar_dados(pokemon)
        else:
            st.warning("Pokémon não encontrado.")

    else:
        st.info(
            "Selecione um Pokémon no PC Storage "
            "ou na área Management."
        )


# =====================================================
# CADASTRO: digita os dados, busca a imagem e grava no BD
# =====================================================
elif pagina == "Cadastro":

    st.header("Cadastrar Pokémon")
    st.write("Digite os dados, busque a imagem e cadastre.")

    numero = int(
        st.number_input(
            "Número da Pokédex",
            min_value=1,
            max_value=1025,
            step=1,
            key="cad_numero"
        )
    )

    # o botão fica fora do form (st.form só aceita botão de envio)
    if st.button("Buscar imagem", key="cad_buscar_imagem"):
        try:
            st.session_state["cad_imagem"] = servico_imagem.baixar_imagem(numero)
            st.session_state["cad_imagem_numero"] = numero
        except ImagemPokemonError as erro:
            st.session_state["cad_imagem"] = None
            st.session_state["cad_imagem_numero"] = None
            st.error(str(erro))

    # só vale a imagem baixada para o número que está na tela agora
    imagem_cadastro = None
    if st.session_state["cad_imagem_numero"] == numero:
        imagem_cadastro = st.session_state["cad_imagem"]

    if imagem_cadastro:
        st.image(imagem_cadastro, width=200)
    else:
        st.info("Nenhuma imagem carregada para esse número.")

    with st.form("cadastro"):

        cad_nome = st.text_input("Nome")
        cad_tipo_um = st.text_input("Primeiro tipo")
        cad_tipo_dois = st.text_input("Segundo tipo (opcional)")
        cad_altura = st.text_input("Altura (opcional)")
        cad_peso = st.text_input("Peso (opcional)")
        cad_descricao = st.text_area("Descrição (opcional)")
        cad_evolucao_antes = st.text_input("Evolução anterior (opcional)")
        cad_evolucao_depois = st.text_input("Próxima evolução (opcional)")

        cadastrar = st.form_submit_button("Cadastrar")

    if cadastrar:

        if not cad_nome.strip():
            st.error("O nome é obrigatório.")

        elif not cad_tipo_um.strip():
            st.error("O primeiro tipo é obrigatório.")

        elif not imagem_cadastro:
            st.error("Busque a imagem antes de cadastrar.")

        else:
            try:
                novo = Pokemon(
                    numero_pokedex=numero,
                    nome=cad_nome.strip(),
                    tipo_um=cad_tipo_um.strip(),
                    tipo_dois=cad_tipo_dois.strip() or None,
                    altura=para_float(cad_altura),
                    peso=para_float(cad_peso),
                    descricao=cad_descricao.strip() or None,
                    imagem=imagem_cadastro,
                    evolucao_antes=cad_evolucao_antes.strip() or None,
                    evolucao_depois=cad_evolucao_depois.strip() or None,
                )

                repositorio.inserir(novo)

                st.session_state["cad_imagem"] = None
                st.session_state["cad_imagem_numero"] = None
                st.success(f"{novo.nome} cadastrado com sucesso!")

            except ValueError:
                st.error("Altura e peso devem ser números válidos.")

            except sqlite3.IntegrityError:
                st.error("Esse número da Pokédex já está cadastrado.")


# =====================================================
# MANAGEMENT: consulta, edição e exclusão
# =====================================================
elif pagina == "Management":

    st.header("Pokémon Management")

    st.subheader("Pesquisar Pokémon")

    with st.form("pesquisa"):

        tipo_busca = st.selectbox(
            "Pesquisar por",
            ["Nome", "Número da Pokédex", "Tipo"]
        )

        pesquisa = st.text_input("Digite sua pesquisa")

        pesquisar = st.form_submit_button("Pesquisar Pokémon")

    if pesquisar:

        if not pesquisa.strip():
            st.warning("Digite algo para pesquisar.")

        else:

            if tipo_busca == "Nome":
                resultados = repositorio.buscar_nome(pesquisa.strip())

            elif tipo_busca == "Número da Pokédex":
                resultados = [
                    p for p in todos_pokemons
                    if str(p.numero_pokedex) == pesquisa.strip()
                ]

            else:
                resultados = repositorio.buscar_tipo(pesquisa.strip())

            st.session_state["resultados"] = resultados

    resultados = st.session_state["resultados"]

    # mostra os resultados
    if resultados:

        st.divider()

        st.subheader("Resultados encontrados")

        for pokemon in resultados:

            with st.container(border=True):

                col1, col2 = st.columns([1, 3])

                with col1:
                    mostrar_imagem(pokemon.imagem, 110)

                with col2:

                    st.subheader(pokemon.nome)

                    st.write("Número:", pokemon.numero_pokedex)
                    st.write("Tipo:", pokemon.tipo_um)

                    if st.button(
                        "Selecionar Pokémon",
                        key=f"selecionar_{pokemon.id}"
                    ):
                        st.session_state["pokemon_selecionado"] = pokemon.id
                        st.rerun()

    elif resultados == []:
        st.info("Nenhum resultado encontrado.")

    # ---------- gerenciar o pokemon selecionado ----------
    id_selecionado = st.session_state["pokemon_selecionado"]

    if id_selecionado:

        pokemon = repositorio.buscar_id(id_selecionado)

        if pokemon:

            st.divider()

            st.header("Gerenciar Pokémon")

            st.write("Selecionado:", pokemon.nome)

            # ----- editar -----
            with st.expander("Editar Pokémon"):

                # botão normal precisa ficar fora do form
                if st.button(
                    "Buscar imagem novamente",
                    key=f"reimg_{pokemon.id}"
                ):
                    try:
                        pokemon.imagem = servico_imagem.baixar_imagem(
                            int(pokemon.numero_pokedex)
                        )
                        repositorio.atualizar(pokemon)
                        st.session_state["resultados"] = None
                        st.success("Imagem atualizada!")
                        st.rerun()

                    except ImagemPokemonError as erro:
                        st.error(str(erro))

                with st.form(f"editar_pokemon_{pokemon.id}"):

                    novo_numero = st.number_input(
                        "Número da Pokédex",
                        min_value=1,
                        max_value=1025,
                        value=int(pokemon.numero_pokedex)
                    )

                    novo_nome = st.text_input("Nome", value=pokemon.nome)

                    novo_tipo_um = st.text_input(
                        "Primeiro tipo",
                        value=pokemon.tipo_um
                    )

                    novo_tipo_dois = st.text_input(
                        "Segundo tipo",
                        value=pokemon.tipo_dois or ""
                    )

                    nova_altura = st.text_input(
                        "Altura",
                        value=str(pokemon.altura or "")
                    )

                    novo_peso = st.text_input(
                        "Peso",
                        value=str(pokemon.peso or "")
                    )

                    nova_descricao = st.text_area(
                        "Descrição",
                        value=pokemon.descricao or ""
                    )

                    nova_evolucao_antes = st.text_input(
                        "Evolução anterior",
                        value=pokemon.evolucao_antes or ""
                    )

                    nova_evolucao_depois = st.text_input(
                        "Próxima evolução",
                        value=pokemon.evolucao_depois or ""
                    )

                    salvar = st.form_submit_button("Salvar alterações")

                if salvar:

                    try:

                        if not novo_nome.strip():
                            st.error("O nome é obrigatório.")

                        elif not novo_tipo_um.strip():
                            st.error("O primeiro tipo é obrigatório.")

                        else:

                            numero_antigo = pokemon.numero_pokedex

                            pokemon.numero_pokedex = int(novo_numero)
                            pokemon.nome = novo_nome.strip()
                            pokemon.tipo_um = novo_tipo_um.strip()
                            pokemon.tipo_dois = novo_tipo_dois.strip() or None
                            pokemon.altura = para_float(nova_altura)
                            pokemon.peso = para_float(novo_peso)
                            pokemon.descricao = nova_descricao.strip() or None
                            pokemon.evolucao_antes = (
                                nova_evolucao_antes.strip() or None
                            )
                            pokemon.evolucao_depois = (
                                nova_evolucao_depois.strip() or None
                            )

                            # se mudou o número, a imagem acompanha a troca
                            if pokemon.numero_pokedex != numero_antigo:
                                pokemon.imagem = servico_imagem.baixar_imagem(
                                    pokemon.numero_pokedex
                                )

                            if repositorio.atualizar(pokemon):
                                st.session_state["resultados"] = None
                                st.success("Pokémon atualizado!")
                                st.rerun()
                            else:
                                st.warning("Não foi possível atualizar.")

                    except ValueError:
                        st.error("Altura e peso devem ser números válidos.")

                    except ImagemPokemonError as erro:
                        st.error(str(erro))

                    except sqlite3.IntegrityError:
                        st.error("Esse número da Pokédex já está cadastrado.")

            # ----- excluir (confirma com checkbox + botão) -----
            with st.expander("Excluir Pokémon"):

                st.warning(f"Deseja excluir {pokemon.nome}?")

                with st.form(f"excluir_pokemon_{pokemon.id}"):

                    confirmar = st.checkbox("Confirmo a exclusão")

                    excluir = st.form_submit_button("Excluir Pokémon")

                if excluir:

                    if confirmar:

                        if repositorio.deletar(pokemon.id):

                            st.session_state["pokemon_selecionado"] = None
                            st.session_state["resultados"] = None

                            st.success("Pokémon excluído com sucesso!")
                            st.rerun()

                        else:
                            st.error("Não foi possível excluir.")

                    else:
                        st.warning("Confirme a exclusão.")
