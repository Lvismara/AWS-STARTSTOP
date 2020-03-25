import boto3
import sys, traceback
from datetime import datetime
from time import sleep

def start_ec2_instances():
    start_time = datetime.now()

    # iniciando ec2 client
    ec2_client = boto3.client('ec2')
    regions = ec2_client.describe_regions()
    
    # pegando os dias da semana e finais de semana
    diaSemana = (start_time.strftime("%a"))
    sabado="Sat"
    domingo="Sun"
    horaBR=start_time.hour-3
    minute=(start_time.strftime("%M"))
    
    print str(horaBR)+':'+str(minute)
    print("Dia: ")
    print(str(diaSemana))
    
    # validacao para nao ligar aos finais de semana
    if diaSemana.lower() != sabado.lower() and diaSemana.lower() != domingo.lower() :
        # loop pelas regioes da aws
        for region in regions['Regions'] :
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
                        
                    if instance['State']['Name'] == "stopped" and HaveTags : 
                        for tag in instance['Tags']:
                            try:
                                if tag['Key'] == 'Start' and tag['Value'] ==  str(horaBR)+':'+str(minute) :
                                    # lista de instancias que serao iniciadas
                                    instanceIds.append(instance['InstanceId'])
                            except:
                                print "Erro nao esperado: ", traceback.print_exc()
                            
            if len(instanceIds) > 0 : 
                # iniciando instancias
                print "iniciando instancias: " + str(instanceIds)
                ec2_client.start_instances(InstanceIds=instanceIds)
                
    end_time = datetime.now()
    took_time = end_time - start_time
    print "Tempo total de execucao: " + str(took_time)     

def lambda_handler(event, context):
    start_ec2_instances()

