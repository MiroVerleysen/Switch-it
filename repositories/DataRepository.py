from .Database import Database

class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_status_actuator():
        sql = "SELECT * from Actuator"
        return Database.get_rows(sql)

    @staticmethod
    def read_status_actuator_by_id(id):
        sql = "SELECT * from Schakelen WHERE actuatorID = %s order by tijdstip desc limit 1"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_status_actuator(id, status):
        sql = "UPDATE Actuator SET status = %s WHERE actuatorID = %s"
        params = [status, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_status_alle_actuator(status):
        sql = "UPDATE Actuator SET status = %s"
        params = [status]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def update_waarde_sensor(id, waarde):
        sql = "Insert into Meetwaarde (sensorid, waarde) values (%s, %s)"
        params = [id, waarde]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_waarde_actuator(id, tijdstip, status):
        sql = "Insert into Schakelen (actuatorid, tijdstip, status) values (%s, %s, %s)"
        params = [id, tijdstip,status]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_all_sensors():
        sql = "select * from Meetwaarde"
        return Database.get_rows(sql)
