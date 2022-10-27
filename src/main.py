import os,telebot 
from telebot.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton
from dotenv import load_dotenv
import re 
import sqlite3

load_dotenv()
bot = telebot.TeleBot(os.environ['api_token'])





##keyboard

    



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
db.execute("CREATE TABLE IF NOT EXISTS account(id_chat,conta,saldo_inicial,date_log)")
db.execute("CREATE TABLE IF NOT EXISTS register(id_chat,conta,type,descricao,valor,date_log)")

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
    

def keyboard_main() :
    global contas 
    contas = read_db('account','conta')
    if len(contas) > 0 :
        keyboard_general =  ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard= True)\
                                        .add(KeyboardButton('Registrar uma Despesa'))\
                                        .add(KeyboardButton('Registrar uma Receita'))\
                                        .add(KeyboardButton('Adicionar Conta'))\
                                        .add(KeyboardButton('Contas'))\
                                        .add(KeyboardButton('Voltar para o Inicio'))
    else : 
        keyboard_general =  ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard= True)\
                                        .add(KeyboardButton('Adicionar Conta'))\
                                        .add(KeyboardButton('Ajuda'))
    return keyboard_general 




def validation_number(mensagem) :
    
    number_regex = re.compile(r"(?:|,|[0-9])*") 
    if re.fullmatch(number_regex, mensagem.text) :
        return mensagem
    else: 
        return False

def contas_keyboard() :
    global keyboard_contas,contas_list
    
    contas = read_db('account','conta')
    contas_list=[]
    keyboard_contas = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard= True)
    for conta in contas:
        keyboard_contas.add(KeyboardButton(f"{conta[0]}"))
        contas_list.append(conta[0])
    print(contas_list)

#####################---Register income/expense----########################################

def description_func(mensagem) :
    global page,description,valor,conta,type
    if page == 'home/register/account/description':
        if type == 'income' :
            bot.reply_to(mensagem,"Obrigado !\n ✅✅✅ Receita Registrada! ✅✅✅")
        else:
            bot.reply_to(mensagem,"Obrigado !\n ✅✅✅ Despesa Registrada! ✅✅✅")
        page = "home"
        chat_id = mensagem.chat.id
        desc = mensagem.text
        date = mensagem.date
        insert_db('register',chat_id,conta,type,desc,valor,date)


@bot.message_handler(func=description_func)

####################################
def despesa(mensagem) :
    global page,valor
    if page == 'home/register/account':
        if validation_number(mensagem) : 
            bot.send_message(mensagem.chat.id,"Qual a descrição?")
            page = "home/register/account/description"
            valor = mensagem.text
        else: 
            bot.reply_to(mensagem,"""Valor Não Aceito tente digitar valores ex: 1234,56""")
            page = 'home/register/account'


@bot.message_handler(func=despesa)
    
####################################
def select_conta(mensagem) :
    global page,type,contas_list,conta
    if  page =='home/register' :
        contas = mensagem.text
        if contas in contas_list :
            print(contas_list)
            page = 'home/register/account'
            conta = mensagem.text
            bot.reply_to(mensagem,"""Qual Valor?""")
        else:
            bot.reply_to(mensagem,"""Conta não reconhecida ! Selecione as opçoes no teclado""",reply_markup = keyboard_contas)
    
@bot.message_handler(func=select_conta)   
######################################

def register_income(mensagem) :
    global page,type,contas
    if mensagem.text == 'Registrar uma Receita' and page =='home' :
        contas_keyboard()
        if len(contas_list) >0 : 
            bot.reply_to(mensagem,"""Escolha uma conta""",reply_markup = keyboard_contas)
            page = 'home/register'
            type = 'income'
        else: 
            bot.send_message(mensagem.chat.id,"""Nenhuma conta Registrada \n Crie uma conta antes de continuar""")
            page = 'home'
        
@bot.message_handler(func=register_income)



def register_expense(mensagem) :
    global page,type
    if mensagem.text == 'Registrar uma Despesa' and page =='home' :
        contas_keyboard()
        if len(contas_list) >0 : 
            bot.reply_to(mensagem,"""Escolha uma conta""",reply_markup = keyboard_contas)
            page = 'home/register'
            type = 'expense'
        else: 
            bot.send_message(mensagem.chat.id,"""Nenhuma conta Registrada \n Crie uma conta antes de continuar""")
            page = 'home'
        
@bot.message_handler(func=register_expense)
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
            insert_db('account',chat_id,nome_conta,conta_saldo,date)

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
para sair é so digitar /sair ou /exit""",reply_markup = keyboard_main())
    


####

def message_general(mensagem):
    global page
    print(f"""mensagem Recebida : {mensagem.text}""")
    print(f"""Pagina = {page}""") 
    if  page == 'home'  :
        return True 

@bot.message_handler(func=message_general)
def responder(mensagem) : 
    bot.reply_to(mensagem,"""Para iniciar Selecione uma opçao abaixo""",reply_markup = keyboard_main())
    

#####################################################################


bot.polling()