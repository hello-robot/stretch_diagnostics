from colorama import Fore, Style
from stretch_production_tools.fleet_definition import  *
import click
import os


def val_in_range(val_name, val, vmin, vmax):
    p = val <= vmax and val >= vmin
    if p:
        print(Fore.GREEN + '[Pass] ' + val_name + ' = ' + str(val))
        print(Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + '[Fail] ' + val_name + ' = ' + str(val) + ' out of range ' + str(vmin) + ' to ' + str(vmax))
        print(Style.RESET_ALL)
        return False


def val_is_not(val_name, val, vnot):
    if val is not vnot:
        print(Fore.GREEN + '[Pass] ' + val_name + ' = ' + str(val))
        return True
    else:
        print(Fore.RED + '[Fail] ' + val_name + ' = ' + str(val))
        return False


def confirm(question: str) -> bool:
    reply = None
    while reply not in ("y", "n"):
        reply = input(Style.BRIGHT + f"{question} (y/n): " + Style.RESET_ALL).lower()
    return (reply == "y")


def print_instruction(text, ret=0):
    return_text = Fore.BLUE + Style.BRIGHT + 'INSTRUCTION:' + Style.RESET_ALL + Style.BRIGHT + text + Style.RESET_ALL
    if ret == 1:
        return return_text
    else:
        print(return_text)


def print_hello_30333_sticker(text_line_1, text_line_2):
    print('Printing sticker with %s : %s'%(text_line_1,text_line_2))
    csv_data='%s, %s\n'%(text_line_1,text_line_2)
    f=open('/tmp/hello_30333.csv',mode='w')
    f.write(csv_data)
    f.write(csv_data)
    f.close()
    os.system('glabels-3-batch /tmp/hello_30333.glabels -i /tmp/hello_30333.csv -o /tmp/hello_30333.pdf')
    os.system('lp -d dymo /tmp/hello_30333.pdf')

def get_robot_sn(batch):
    #  'mitski':{'start_sn':2000, 'end_sn':2025,'model':'RE2V0','model_name':'stretch-re2'}}
    while True:
        sn=click.prompt('Enter the robot serial no (eg. 2001 for stretch-re2-re1)', type=int)
        if sn>=fleet_definition[batch]['start_sn'] and sn<=fleet_definition[batch]['end_sn']:
            robot_sn=fleet_definition[batch]['model_name']+'-'+str(sn)
            print('Proceeding with robot: %s'%robot_sn)
            return robot_sn
        else:
            print('Invalid entry. For batch %s serial number must be between %d and %d'%(batch,fleet_definition[batch]['start_sn'] , fleet_definition[batch]['end_sn']))

def print_bright(text):
    print(Style.BRIGHT + Fore.BLUE + text + Style.RESET_ALL)

def print_bright_red(text):
    print(Style.BRIGHT + Fore.RED + text + Style.RESET_ALL)