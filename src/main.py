import os,telebot 
from telebot.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton
from dotenv import load_dotenv
import re 
import sqlite3

load_dotenv()
bot = telebot.TeleBot(os.environ['api_token'])





##keyboard

    
keyboard_general = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard= True)\
                                        .add(KeyboardButton('Registrar uma Despesa'))\
                                        .add(KeyboardButton('Registrar uma Receita'))\
                                        .add(KeyboardButton('Adicionar Conta'))\
                                        .add(KeyboardButton('Contas'))\
                                        .add(KeyboardButton('Voltar para o Inicio'))



page = 'home'
chat_id = ''
date = ''
description = ''
value = []
type = []
conta_new = []
account_verifica = []
conta_saldo = []



print("------------BOT INICIADO------------")
##########################Global_functions###########################################

con = sqlite3.connect("./bot.db" ,check_same_thread=False)
db = con.cursor()
#db.execute("DROP TABLE bot")
db.execute("CREATE TABLE IF NOT EXISTS bot(id_chat,conta,saldo_inicial,date_log)")
db.execute("CREATE TABLE IF NOT EXISTS registros(id_chat,conta,descricao,valor,date_log)")

def insert_db(table,*args):
    print('-'*50+'INSERT IN DB'+'-'*50)
    print(f"""INSERT INTO {table} VALUES {args}""")
    db.execute(f"""INSERT INTO {table} VALUES{args}""")
    con.commit()
    print('INSERTED')

def read_db(table,columns = '*') :
    print('-'*50+'READ DB'+'-'*50)
    print(f"SELECT {columns} FROM {table}")
    db.execute(f"SELECT {columns} FROM {table}")
    return db.fetchall()
    
def print_db(table,columns = '*') : 
    print('-'*50+'TABELA'+'-'*50)
    db.execute(f"SELECT {columns} FROM {table}")
    table = db.fetchall() 
    print(table)
    print('-'*50)
    


def validation_number(mensagem) :
    
    number_regex = re.compile(r"(?:|,|[0-9])*") 
    if re.fullmatch(number_regex, mensagem.text) :
        return mensagem
    else: 
        return False

def contas_keyboard() :
    global keyboard_contas,contas_list
    
    contas = read_db('bot','conta')
    contas_list=[]
    keyboard_contas = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard= True)
    for conta in contas:
        keyboard_contas.add(KeyboardButton(f"{conta[0]}"))
        contas_list.append(conta[0])
    print(contas_list)

##################### expenseive ################################################

def description_func(mensagem) :
    global page,description,valor,conta
    if page == 'home/despesa/conta/description':
        bot.reply_to(mensagem,"Obrigado ! Despesa Registrada! ✅✅✅")
        page = "home"
        chat_id = mensagem.chat.id
        desc = mensagem.text
        date = mensagem.date
        insert_db('registros',chat_id,conta,desc,valor,date)


@bot.message_handler(func=description_func)

#####################################################################
def despesa(mensagem) :
    global page,valor
    if page == 'home/despesa/conta':
        if validation_number(mensagem) : 
            bot.send_message(mensagem.chat.id,"Qual a descrição para essa Despesa?")
            page = "home/despesa/conta/description"
            valor = mensagem.text
        else: 
            bot.reply_to(mensagem,"""Valor Não Aceito tente digitar valores ex: 1234,56""")
            page = 'home/despesa/conta'


@bot.message_handler(func=despesa)
    
####################################
def select_conta(mensagem) :
    global page,type,contas_list,conta
    if  page =='home/despesa' :
        contas = mensagem.text
        if contas in contas_list :
            print(contas_list)
            page = 'home/despesa/conta'
            conta = mensagem.text
            bot.reply_to(mensagem,"""Qual Valor?""")
        else:
            bot.reply_to(mensagem,"""Conta não reconhecida ! Selecione as opçoes no teclado""",reply_markup = keyboard_contas)
    
@bot.message_handler(func=select_conta)   
#####################################################################

def registrar_despesa(mensagem) :
    global page,type
    if mensagem.text == 'Registrar uma Despesa' and page =='home' :
        contas_keyboard()
        bot.reply_to(mensagem,"""Escolha uma conta""",reply_markup = keyboard_contas)
        page = 'home/despesa'
        
@bot.message_handler(func=registrar_despesa)
###

    
#############################--VIEW ACCOUNT--########################################

def account(mensagem) :
    global page
    if mensagem.text == 'Contas' and page =="home" :
        page = 'home/contas'
        contas_keyboard()
        bot.reply_to(mensagem,f"""Selecione a conta!""",reply_markup = keyboard_contas)   

        
@bot.message_handler(func=account) 
#############################--ADD ACCOUNT AND SALES--########################################

def account_saldo(mensagem) :
    global page,conta_saldo,chat_id,date
    if page == 'home/conta/name' :
       if validation_number(mensagem) :
            bot.reply_to(mensagem,"Conta Adicionada com Sucesso!")
            page ='home'
            chat_id = mensagem.chat.id
            date = mensagem.date
            conta_saldo = mensagem.text
            bot.send_message(mensagem.chat.id,f"""seu saldo na {nome_conta} é de {conta_saldo} R$!""")
            insert_db('bot',chat_id,nome_conta,conta_saldo,date)

            return True
       else :
            bot.reply_to(mensagem,"Valor não é valido digite novamente!")
            page = 'home/conta/name'
        
@bot.message_handler(func=account_saldo)
    

    ######################

def account_verificar(mensagem) :
    global page,nome_conta
    if page == 'home/conta' :
        nome_conta = mensagem.text  
        page = 'home/conta/name'
        print(nome_conta)
        bot.reply_to(mensagem,f"""Qual o Saldo da conta {nome_conta}?""")
        return True

@bot.message_handler(func=account_verificar)

####

def account(mensagem) :
    global page,type
    if mensagem.text == 'Adicionar Conta' and page =="home" :
        page = 'home/conta'
        bot.reply_to(mensagem,"""Qual o nome da Conta?""")   

        
@bot.message_handler(func=account) 
 

#############################--MAIN MENU--########################################

@bot.message_handler(commands = ["/sair","/exit"])
def sair(mensagem) :
    global page
    page= 'home'


@bot.message_handler(commands = ["start"])
def boas_vindas(mensagem) :
    global chat_id,page

    bot.send_message(mensagem.chat.id, """Seja Bem vindo ao meu bot de finaças!
para usa-lo pressione as opçoes abaixo
para sair é so digitar /sair ou /exit""",reply_markup = keyboard_general)
    


####

def message_general(mensagem):
    global page
    print(f"""mensagem Recebida : {mensagem.text}""")
    print(f"""Pagina = {page}""") 
    if  page == 'home'  :
        return True 

@bot.message_handler(func=message_general)
def responder(mensagem) : 
    bot.reply_to(mensagem,"""Para iniciar Selecione uma opçao abaixo""",reply_markup = keyboard_general)
    

#####################################################################


bot.polling()