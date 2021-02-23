class CSVTimeSeriesFile:

    def __init__(self, name):
        self.name = name

    # metodo usato per estrarre i campi dal record "line"
    def data_from_line(self, line):
        fields = line.strip().split(",")
        try:
            if len(fields) < 2: # controllo che il record abbia almeno due campi
                return None
            # prendo solo i primi due campi del record
            fields[0] = round(float(fields[0]))
            fields[1] = float(fields[1])
            
            return fields
        except ValueError: # nel caso in cui i campi non siano numerici
            return None

    def get_data(self):
        if (self.name is None) or (len(self.name) == 0) or (not isinstance(self.name, str)):
            raise ExamException("Nome del file non valido.")

        try:
            csv_file = open(self.name, "r")
        except: # nel caso si presentino problemi con l'apertura del file
            raise ExamException("Impossibile leggere il file.")

        data = []
        for line in csv_file:
            fields = self.data_from_line(line)
            if fields is None: # se il record non e' valido lo salto
                continue
            data_len = len(data)
            if data_len > 0 and fields[0] <= (data[data_len-1])[0]: # confronto l'epoch attuale con quello precedente (se presente)
                raise ExamException("Piu' temperature per lo stesso epoch oppure epoch non in ordine.")
            data.append(fields)

        csv_file.close()
        return data

class ExamException(Exception):
    pass

def hourly_trend_changes(time_series):
    trend = [] # lista tornata dalla funzione, contiene le inversioni 
    idx = 0 # indice per scorrere la lista 'time_series'
    idx_trending = -1 # indice della lista 'trend', e' di fatto l'ora (nella PRIMA ora ci sono state tot inversioni... nella SECONDA...)
    prec_hour_considered = -1 # ora considerata ad un'iterazione precedente
    increasing = False # boolean per tenere conto della crescenza della temperatura

    if len(time_series) == 1: # con un solo dato abbiamo zero inversioni
        return [0]

    while(idx < len(time_series)-1): # ciclo fino a quando non finisco i dati
        hour = (time_series[idx+1][0])//3600 # prendo l'ora a partire dal epoch
        if(prec_hour_considered != hour): # controllo se ho cambiato ora di riferimento delle temperature
            idx_trending += 1 # aumento l'indice (l'ora a cui si riferiscono le inversioni) della lista 'trend'
            trend.append(0) # aggiungo zero (ovvero il numero delle inversioni) alla lista
        prec_hour_considered = hour

        if(time_series[idx][1] > time_series[idx+1][1]): # controllo se la temperatura scende
            if(increasing and idx != 0): # controllo se ho subito un'inversione del trend
                trend[idx_trending] += 1
            increasing = False # la temperatura non sta salendo piu'
        if(time_series[idx][1] < time_series[idx+1][1]): # controllo se la temperatura sale
            if(not increasing and idx != 0):
                trend[idx_trending] += 1
            increasing = True

        idx += 1

    return trend    

#if __name__ == "__main__":
    #tsf = CSVTimeSeriesFile(name="data.csv")
    #dati = tsf.get_data()
    #print(hourly_trend_changes(dati))