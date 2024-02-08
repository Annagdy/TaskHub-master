import sys
import typing
import ast
import re

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget, QTableWidget, QTableWidgetItem, QCheckBox, QAbstractItemView, QHeaderView, QDateEdit

from login_tela import Login_Tela
from cadastro_tela import Cadastro_Tela
from tela_principal import Tela_Principal
from tarefa import Tela_Tarefa
from pessoa import Pessoa
from cadastro import Cadastro
from login import Login
from task import Tarefa
from cliente import Cliente

import mysql.connector
from mysql.connector import Error
import pandas as pd
import json
import datetime
from datetime import date

from database import create_db_connection, create_server_connection, execute_query

class Ui_Main(QtWidgets.QWidget):
    def setupUi(self, Main):
        Main.setObjectName("TaskHub")
        Main.setWindowTitle("TaskHub")
        
        self.Qtstack = QtWidgets.QStackedLayout()

        self.stack0 = QtWidgets.QMainWindow()
        self.stack1 = QtWidgets.QMainWindow()
        self.stack2 = QtWidgets.QMainWindow()
        self.stack3 = QtWidgets.QMainWindow()

        self.login_tela = Login_Tela()
        self.login_tela.setupUi(self.stack0)
        self.login_tela.senha_linha.setEchoMode(self.login_tela.senha_linha.Password)

        self.cadastro_tela = Cadastro_Tela()
        self.cadastro_tela.setupUi(self.stack1)
        self.cadastro_tela.senha_linha.setEchoMode(self.cadastro_tela.senha_linha.Password)

        self.tela_principal = Tela_Principal()
        self.tela_principal.setupUi(self.stack2)

        self.tarefa = Tela_Tarefa()
        self.tarefa.setupUi(self.stack3)

        self.Qtstack.addWidget(self.stack0)
        self.Qtstack.addWidget(self.stack1)
        self.Qtstack.addWidget(self.stack2)
        self.Qtstack.addWidget(self.stack3)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

class Main(QMainWindow, Ui_Main):
    """
    Classe principal que controla a interface do usuário do TaskHub.

    Methods
    -------
    __init__(self)
        Construtor da classe. Inicializa a interface e conecta sinais aos slots.
    botaoCriaTarefa(self)
        Manipula o botão de criar tarefa, inserindo uma nova tarefa no banco de dados.
    usuarioExiste(self, usuario_email)
        Verifica se um usuário com o email especificado já existe no banco de dados.
    botaoCadastra(self)
        Manipula o botão de cadastrar, enviando informações para o servidor e exibindo mensagens.
    botaoLogin(self)
        Manipula o botão de login, enviando informações para o servidor e exibindo mensagens.
    botaoCriar(self)
        Muda para a tela de criação de tarefas.
    telaPrinc(self)
        Retorna para a tela principal.
    returnIndex(self)
        Retorna para a tela de login.
    abrirTelaCadastro(self)
        Muda para a tela de cadastro.
    abrirTelaPrincipal(self)
        Muda para a tela principal.
    """

    def __init__(self):
        super(Main, self).__init__(None)
        self.setupUi(self)

        self.usuario_logado = None
        self.username = None
        self.cliente = Cliente()
        self.cad = Cadastro()

        self.login_tela.confirmarLogin.clicked.connect(self.botaoLogin)
        self.login_tela.cadastrar.clicked.connect(self.abrirTelaCadastro)
        self.login_tela.fecharBota.clicked.connect(exit)

        self.cadastro_tela.confirmar.clicked.connect(self.botaoCadastra)
        self.cadastro_tela.voltarBotao.clicked.connect(self.returnIndex)

        self.tela_principal.pushButton.clicked.connect(self.returnIndex)

        self.tela_principal.Criar.clicked.connect(self.botaoCriar)
        
        self.tarefa.cancel.clicked.connect(self.telaPrinc)

        self.tarefa.conf.clicked.connect(self.botaoCriaTarefa)

        # self.login_tela.confirmarLogin.clicked.connect(exibir_tarefas(self))

        # # self.login_tela.confirmarLogin.clicked.connect(exibir_tarefas(self))

        # self.tarefa.conf.clicked.connect(mostrar_tarefas(self))

        self.login_tela.confirmarLogin.clicked.connect(self.mostrar_tarefas)

        self.tarefa.conf.clicked.connect(self.mostrar_tarefas)

        self.tela_principal.excluir_tarefa.clicked.connect(self.botaoExcluirTarefa)

    def mostrar_tarefas(self):
        
        #Obtenha o email do usuário logado
        usuario_email = self.login_tela.email_linha.text()

        # Obtenha as tarefas do usuário
        tarefas = self.cliente.enviar('5' + '-' + usuario_email)


        # Junte a string e remova os caracteres desnecessários'
        tarefas_str = ''.join(tarefas).replace('[(', '').replace(')]', '')
        padrao = r"datetime\.date\((\d+),\s*(\d+),\s*(\d+)\)"
        tarefas = re.sub(padrao, r"'\1/\2/\3'", tarefas)
        tarefas = tarefas.replace("'", '"')
        
        tarefas = json.loads(tarefas)
        print(f"tarefas: {tarefas}")
        
        self.tela_principal.listaTodo.setRowCount(len(tarefas))
        self.tela_principal.listaTodo.setColumnCount(6)

        
        self.tela_principal.listaTodo.setHorizontalHeaderLabels(['Título', 'Data Final', 'Prioridade', 'Status', 'Descrição','Criador'])
        
    
        #mudar largura das colunas
        self.tela_principal.listaTodo.setColumnWidth(0, 250)
        self.tela_principal.listaTodo.setColumnWidth(1, 150)
        self.tela_principal.listaTodo.setColumnWidth(2, 120)
        self.tela_principal.listaTodo.setColumnWidth(3, 120)
        self.tela_principal.listaTodo.setColumnWidth(4, 400)
        self.tela_principal.listaTodo.setColumnWidth(5, 150)
        
        # Coloque os dados na tabela
        for i in range (0, len(tarefas)):
            self.tela_principal.listaTodo.setItem(i, 0, QTableWidgetItem(tarefas[i]["titulo"]))
            self.tela_principal.listaTodo.setItem(i, 1, QTableWidgetItem(tarefas[i]["data_final"]))
            self.tela_principal.listaTodo.setItem(i, 2, QTableWidgetItem(tarefas[i]["prioridade"]))
            self.tela_principal.listaTodo.setItem(i, 3, QTableWidgetItem(tarefas[i]["status"]))
            self.tela_principal.listaTodo.setItem(i, 4, QTableWidgetItem(tarefas[i]["descricao"]))
            self.tela_principal.listaTodo.setItem(i, 5, QTableWidgetItem(tarefas[i]["usuario_email"]))

    
        

    
    def botaoCadastra(self):
        usuario = self.cadastro_tela.usuario_linha.text()
        email = self.cadastro_tela.email_linha.text()
        senha = self.cadastro_tela.senha_linha.text()

        if not(usuario == '' or email == '' or senha == '' or usuario == ' ' or email == ' ' or senha == ' '):

            msg = '1' + '-' + usuario + '-' + email + '-' + senha

            recebeu = self.cliente.enviar(msg)
            if recebeu == '1':
                QMessageBox.information(None, 'TaskHub', 'Cadastro Realizado com Sucesso!')
                self.cadastro_tela.usuario_linha.setText('')
                self.cadastro_tela.email_linha.setText('')
                self.cadastro_tela.senha_linha.setText('')
                self.Qtstack.setCurrentIndex(0)
            else:
                QMessageBox.information(None, 'TaskHub', 'Email já cadastrado!')
                self.cadastro_tela.usuario_linha.setText('')
                self.cadastro_tela.email_linha.setText('')
                self.cadastro_tela.senha_linha.setText('')
        else:
            QMessageBox.information(None, 'TaskHub', 'Preencha Todos os Campos!')
            self.cadastro_tela.usuario_linha.setText('')
            self.cadastro_tela.email_linha.setText('')
            self.cadastro_tela.senha_linha.setText('')

    def botaoLogin(self):
        email = self.login_tela.email_linha.text()
        senha = self.login_tela.senha_linha.text()

        mensagem = '0' + '-' + email + '-' + senha
        resposta = self.cliente.enviar(mensagem)

        if resposta != '0':
            #pegar nome do usuario
            username = self.cliente.enviar('2' + '-' + email + '-' + senha)

            # Obtenha o email do usuário logado
            usuario_email = self.login_tela.email_linha.text()

            # Obtenha as tarefas do usuário
            tarefas = self.cliente.enviar('5' + '-' + usuario_email)


            print(str(len(tarefas)) + 'aqui')

            # for i in range (0, len(tarefas)):
            #     for j in range (0, 6):
            #         self.tela_principal.listaTodo.setItem(i, j, QTableWidgetItem(tarefas[i][j]))

            

            QMessageBox.information(None, 'TaskHub', 'Login Realizado com Sucesso!')
            self.Qtstack.setCurrentIndex(2)
            self.tela_principal.linha_user.setText(username)
            self.login_tela.senha_linha.setText('')
        else:
            QMessageBox.information(None, 'TaskHub', 'Email ou Senha Incorretos!')
        
        

            

    def botaoCriaTarefa(self):
        usuario_email = self.login_tela.email_linha.text()

        # Verifique se o usuário existe antes de criar a tarefa
        usuario_existe = self.cliente.enviar('4' + '-' + usuario_email)
        
        # Inicialize 'recebeu' antes do bloco try
        recebeu = None
        
        try:
            if usuario_existe == '1':
                
                # Crie a tarefa
                titulo = self.tarefa.title_tarefa.text()
                descricao = self.tarefa.descricao_tarefa.toPlainText()
                # Correção: Converta QDate para string usando toString
                data_final = self.tarefa.data_tarefa.date().toString('yyyy/MM/dd')
            

                prioridade = self.tarefa.prioridade_tarefa.currentText()
                grupo = self.tarefa.group_tarefa.text()
                status = self.tarefa.status_tarefa.currentText()
            
                msg = '3' + '-' + titulo + '-' + descricao + '-' + data_final + '-' + prioridade + '-' + grupo + '-' + status + '-' + usuario_email

                # Atualize 'recebeu' aqui
                recebeu = self.cliente.enviar(msg)

            # Verifique o valor de 'recebeu' aqui e tome as ações apropriadas
            if recebeu == '1':
                QMessageBox.information(None, 'TaskHub', 'Tarefa criada com sucesso!')
            else:
                QMessageBox.information(None, 'TaskHub', 'Erro ao criar tarefa. Tente novamenteeee.')

        except Exception as e:
            print(f"Erro ao criar tarefa: {e}")
        
    def botaoExcluirTarefa(self):
        #quero que exclua a tarefa clicada com base no id dela

        # Obtenha o email do usuário logado
        usuario_email = self.login_tela.email_linha.text()

        # Obtenha as tarefas do usuário
        tarefas = self.cliente.enviar('5' + '-' + usuario_email)

        # Obtenha o índice da linha selecionada
        linha_selecionada = self.tela_principal.listaTodo.currentRow()

        # Obtenha o id da tarefa selecionada
        id_tarefa = tarefas[linha_selecionada][0]

        # Exclua a tarefa
        recebeu = self.cliente.enviar('6' + '-' + id_tarefa)

        if recebeu == '1':
            QMessageBox.information(None, 'TaskHub', 'Tarefa excluída com sucesso!')
        else:
            QMessageBox.information(None, 'TaskHub', 'Erro ao excluir tarefa. Tente novamente.')

        

    def botaoCriar(self):
        self.Qtstack.setCurrentIndex(3)
    
    def telaPrinc(self):
        self.Qtstack.setCurrentIndex(2)
        

    def returnIndex(self):
        self.Qtstack.setCurrentIndex(0)

    def abrirTelaCadastro(self):
        self.Qtstack.setCurrentIndex(1)

    def abrirTelaPrincipal(self):
        self.Qtstack.setCurrentIndex(2)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    show_main = Main()

    sys.exit(app.exec_())
   
    