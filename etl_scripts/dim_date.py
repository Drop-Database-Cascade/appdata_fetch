from dim_table_class import dim_table_local_file_operations

#This creates a date dimension table as a csv which contains daily dates between 1 Jan 2010 and an end date passed as a parameter. The columns produced are Index, date_key, date, 
#year, month(int), day, month(str). file name is the path to csv location

def get_date_dim(end_date:str):
    
    try:
        #Main Function
        dim = dim_table_local_file_operations()
        year, month, day = dim.get_date_int(end_date)
        dim.write_dates_to_csv('dim_date.csv', year, month, day)
        return True
        
    except Exception as e:
        raise(e)

def main():
    get_date_dim("2022-12-31")

if __name__ == "__main__":
    main()