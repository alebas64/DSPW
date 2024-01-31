
# nome dei topic del sistema
TOPIC_BOTCOMMANDS = "Bot_Command"
TOPIC_BOTMESSAGE = "Bot_Message"
TOPIC_BOTNOTIFIER = "Bot_Notifier"
TOPIC_APIPARAMS = "Api_Params"
TOPIC_METEOPREVISION = "Meteo_Prevision"
TOPIC_METEORESULTS = "Meteo_Results"
TOPIC_METEOCOMMANDS = "Meteo_Commands"
TOPIC_REQUESTCONSTRAINT = "Request_Constraint"
TOPIC_RESPONSECONSTRAINT = "Response_Constraint"
TOPIC_COORDSRESULT="Coords_Result"
TOPIC_NEWCONSTRAINTS="New_Constraints"
# TOPIC_ = "" # se mai si debba aggiungere un topic

# chiave per comunicazioni

#topic:Bot_notifier
KEY_SU_TBC="risultati_sqluser" #sqluser -> telegrambotconstructor
KEY_SOL_TBC="risultati_sqloplist" #sqlOperationList -> telegramBotConstructor
KEY_UP_TBC="risultati_userprevision" #userPrevision -> telegramBotConstructor
KEY_TBR_TBC="risultati_telegramReader" #telegramBotReader -> telegramBotConstructor
KEY_SOC_TBC="risultati_sqlOpConstraint" #sqlOperationConstraint -> telegramBotConstructor

#topic:Api_Params
KEY_SOL_OW="richiesta_previsione" #SqlOperationList->Openweather
KEY_SOC_OW="richiesta_coordinate"  #SqlOperationConstraint-> OpenWeather

#topic:Meteo_Commands
KEY_SOL_MI="Clear"

#topic: Meteo_Results
KEY_MO_UP="Results" #MongoOutput-> UserPrevision

#topic New_Constraints
KEY_SOL_UP="Nuovo_Constraint" #SqlOperationList-> UserPrevision

#Topic: BotCommands
KEY_TBR_SOL="richiesta_liste"

# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = ""
# KEY_ = "" # se mai si debba aggiungere una key



# partizione per comunicazioni


#topic:Bot_command
PARTITION_TBR_SOC = 0 # telegrambotreader -> slqoperationconstraint
PARTITION_TBR_SOL = 1 # telegrambotreader -> sqloperationlist
PARTITION_TBR_SU = 2 # telegrambotreader -> sqluser



#topic:Meteo_Commands 
PARTITION_SOL_MI=0  #SqlOperationList->MongoInput
PARTITION_UP_MO=1   #UserPrevision-> MongoOutput

#topic:Response_Constraint 
PARTITION_SOL_UP=0  #SqlOperationList -> UserPrevision
PARTITION_SOC_SOL=1 #SqlOperationConstraint->SqlOperationList


# PARTITION_ = ""
# PARTITION_ = ""
# PARTITION_ = ""
# PARTITION_ = ""
# # PARTITION_ = "" # se mai si debba aggiungere una partizione



