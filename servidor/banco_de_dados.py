import mysql.connector as mysql
import datetime
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox
import ast

class Banco:
    def __init__(self) -> None:
        """
        Construtor da classe Banco.

        Este construtor inicializa a conexão com o banco de dados MySQL, cria as tabelas necessárias,
        e inicializa algumas variáveis de controle.

        Attributes
        ----------
        conexao : mysql.connector.connection
            Objeto de conexão com o banco de dados.
        cursor : mysql.connector.cursor
            Cursor para executar comandos SQL.
        usuario_logado : str
            Email do usuário logado, inicializado como None.

        Tables
        ------
        User : Tabela para armazenar informações do usuário.
            Campos: user_name, email, senha.

        tarefas : Tabela para armazenar informações das tarefas.
            Campos: id, descricao, status, usuario_email (referência à tabela User).

        """
        self.conexao = mysql.connect(host='localhost', database='poo2', user='root', password='z321')
        self.cursor = self.conexao.cursor()

        self.usuario_logado = None

        # Criação das tabelas se não existirem
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                        user_name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) PRIMARY KEY NOT NULL,
                        senha VARCHAR(100) NOT NULL
                     )''')
        
        self.conexao.commit()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tarefas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            descricao VARCHAR(500) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Pendente',
            usuario_email VARCHAR(100),
            FOREIGN KEY (usuario_email) REFERENCES User(email),
            data_final DATE NOT NULL,
            grupo VARCHAR(20) NOT NULL,
            titulo VARCHAR(100) NOT NULL,
            prioridade VARCHAR(20) NOT NULL
        )''')
        
        self.conexao.commit()
        
    def cadastrar_usuario(self, user_name, email, senha):
        """
        Cadastra um novo usuário no banco de dados.

        Parameters
        ----------
        user_name : str
            Nome do usuário.
        email : str
            Email do usuário (chave primária).
        senha : str
            Senha do usuário.

        Returns
        -------
        bool
            Retorna True se o cadastro for bem-sucedido, False caso contrário.
        """
        try:
            self.cursor.execute(f"INSERT INTO user VALUES ('{email}', '{user_name}', '{senha}')")
            self.conexao.commit()
            return True
        except Exception as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return False

    
    def obter_email_usuario_logado(self):
        """
        Obtém o email do usuário logado.

        Returns
        -------
        str or None
            Retorna o email do usuário logado ou None se nenhum usuário estiver logado.
        """
        if self.usuario_logado is not None:
            return self.usuario_logado
        return None
    
    def obter_nome_usuario_logado(self):
        """
        Obtém o nome do usuário logado.

        Returns
        -------
        str or None
            Retorna o nome do usuário logado ou None se nenhum usuário estiver logado.
        """
        if self.usuario_logado is not None:
            self.cursor.execute(f"SELECT user_name FROM User WHERE email = '{self.usuario_logado}'")
            resultado = self.cursor.fetchone()
            if resultado is not None:
                return resultado[0]
        return None

    def logar_usuario(self, email, senha):
        """
        Realiza o login de um usuário.

        Parameters
        ----------
        email : str
            Email do usuário.
        senha : str
            Senha do usuário.

        Returns
        -------
        bool
            Retorna True se o login for bem-sucedido, False caso contrário.
        """
        self.cursor.execute(f"SELECT * FROM User WHERE email = '{email}' AND senha = '{senha}'")
        resultado = self.cursor.fetchone()
        if resultado is not None:
            self.usuario_logado = email
            return True
        return False
    
    def usuarioExiste(self, usuario_email):
        """
        Verifica se um usuário existe.

        Parameters
        ----------
        usuario_email : str
            Email do usuário.

        Returns
        -------
        bool
            Retorna True se o usuário existir, False caso contrário.
        """
        self.cursor.execute(f"SELECT * FROM User WHERE email = '{usuario_email}'")
        resultado = self.cursor.fetchone()
        if resultado is not None:
            return True
        return False
    
    def emailExiste(self, email):
        """
        Verifica se um email existe.

        Parameters
        ----------
        email : str
            Email do usuário.

        Returns
        -------
        bool
            Retorna True se o email existir, False caso contrário.
        """
        self.cursor.execute(f"SELECT * FROM User WHERE email = '{email}'")
        resultado = self.cursor.fetchone()
        if resultado is not None:
            return True
        return False
    
    def cadastrar_tarefa(self, titulo, descricao, data_final, prioridade, grupo, status, usuario_email):
        """
        Cadastra uma nova tarefa no banco de dados.

        Parameters
        ----------
        titulo : str
            Título da tarefa.
        descricao : str
            Descrição da tarefa.
        data : str
            Data de conclusão da tarefa.
        prioridade : str
            Prioridade da tarefa.
        grupo : str
            Grupo da tarefa.
        status : str
            Status da tarefa.
        usuario_email : str
            Email do usuário que cadastrou a tarefa.

        Returns
        -------
        bool
            Retorna True se o cadastro for bem-sucedido, False caso contrário.
        """
        from datetime import datetime

        # Adicionando o dia e mês padrão ('01-01') se apenas o ano foi fornecido
        if len(data_final) == 4:
            data_final = data_final + '-01-01'

        try:
            data_final = datetime.strptime(data_final, '%Y-%m-%d')
            self.cursor.execute(f"INSERT INTO tarefas (descricao, status, usuario_email, data_final, grupo, titulo, prioridade) VALUES ('{descricao}', '{status}', '{usuario_email}', '{data_final}', '{grupo}', '{titulo}', '{prioridade}')")
            self.conexao.commit()
            return '1'
        except Exception as e:
            print(f"Erro ao cadastrar tarefa: {e}")
            return '0'
            
    def obter_tarefas(self, usuario_email):
        """
        Obtém todas as tarefas de um usuário.

        Parameters
        ----------
        usuario_email : str
            Email do usuário.

        Returns
        -------
        list
            Lista de tarefas do usuário.
        """
        try:
            self.cursor.execute("SELECT * FROM tarefas WHERE usuario_email = %s", (usuario_email,))
            # Armazenar as tarefas e enviar
            tarefas = self.cursor.fetchall()

            # Processar as tarefas e acessar as colunas individualmente
            tarefas_formatadas = []
            for tarefa in tarefas:
                # Cada tarefa é uma tupla, e você pode acessar os valores das colunas pelo índice
                id_tarefa = tarefa[0]
                descricao = tarefa[1]
                status = tarefa[2]
                usuario_email = tarefa[3]
                data_final = tarefa[4]
                grupo = tarefa[5]
                titulo = tarefa[6]
                prioridade = tarefa[7]

                # Criar um dicionário ou uma tupla com os valores das colunas, conforme necessário
                tarefa_formatada = {
                    "id": id_tarefa,
                    "descricao": descricao,
                    "status": status,
                    "usuario_email": usuario_email,
                    "data_final": data_final,
                    "grupo": grupo,
                    "titulo": titulo,
                    "prioridade": prioridade
                }

                tarefas_formatadas.append(tarefa_formatada)
                
            print(tarefas_formatadas)

            return tarefas_formatadas
        except Exception as e:
            print(f"Erro ao obter tarefas: {e}")
            return None

    def excluir_tarefa(self, id_tarefa):
        """
        Exclui uma tarefa do banco de dados.

        Parameters
        ----------
        id_tarefa : int
            ID da tarefa.

        Returns
        -------
        bool
            Retorna True se a exclusão for bem-sucedida, False caso contrário.
        """
        try:
            self.cursor.execute("DELETE FROM tarefas WHERE id = %s", (id_tarefa,))
            self.conexao.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir tarefa: {e}")
            return False
        
    
        

