import boto3
import sys, traceback
from datetime import datetime
from time import sleep

def stop_ec2_instances():
    start_time = datetime.now()

    # starting ec2 client
    ec2_client = boto3.client('ec2')
    regions = ec2_client.describe_regions()
    
    diaSemana = (start_time.strftime("%a"))
    sabado="Sat"
    domingo="Sun"
    
    print("Hora GMT inicio: "+str(start_time.hour))
    # Validação necessaria para evitar stop de sextafeira a noite
    horaBR=start_time.hour-3
     
    if(horaBR==-3):
        horaBR=21
        if diaSemana.lower() == sabado.lower():
            diaSemana="Fri"
    if(horaBR==-2):
        horaBR=22
        if diaSemana.lower() == sabado.lower():
            diaSemana="Fri"
    if(horaBR==-1):
        horaBR=23
        if diaSemana.lower() == sabado.lower():
            diaSemana="Fri"
       
    minute=(start_time.strftime("%M"))
    
    print("Hora Brasilia inicio: ")
    print(str(horaBR)+':'+str(minute))
    
    print("Dia: ")
    print(str(diaSemana))
    
    # validacao para nao ligar aos finais de semana
    if diaSemana.lower() != sabado.lower() and diaSemana.lower() != domingo.lower() :
        # loop pelas regioes da aws
        for region in regions['Regions']:
            print(region['RegionName'])
            ec2_client = boto3.client('ec2', region_name=region['RegionName'])
            # armazenando as instancias pela regiao
            instances = ec2_client.describe_instances()
            instanceIds = list()
                    
            # processo de verificação de tag
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    try:
                        tag=instance['Tags']
                        HaveTags= True                
                    except:
                        HaveTags= False  
                        
                    if instance['State']['Name'] == "running" and HaveTags : 
                        for tag in instance['Tags']:
                            try:
                                if tag['Key'] == 'Stop' and tag['Value'] == str(horaBR)+':'+str(minute):
                                    # lista de instancias que serao paradas
                                    instanceIds.append(instance['InstanceId'])
                            except:
                                print "Erro nao esperado: ", traceback.print_exc()
                              
            # parando instancias                              
            if len(instanceIds) > 0 : 
                print "parando instancias: " + str(instanceIds)
                ec2_client.stop_instances(InstanceIds=instanceIds, Force=False)
                                                               
        end_time = datetime.now()
        took_time = end_time - start_time
        print "Tempo total de execucao: " + str(took_time)     

def lambda_handler(event, context):
    stop_ec2_instances()

