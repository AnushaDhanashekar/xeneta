# xeneta
1. database schema is same as part of the given assignment, it has got 3 tables, Ports, Regions and Prices

2. connected to an exposed Postgres instance on the Docker host IP address of '192.168.99.100'
3. please do change '192.168.99.100' to corresponding localhost which is usually *127.0.0.1* or *172.17.0.1* while you run this application in your local machine 
   configure IP in file main.py at line number 12, 15
4. use 'python main.py' to execute the file
5. http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-02&origin=CNGGZ&destination=EETLL 
6. Use URL mentioned above to check the sample output
7. for the URL in mentioned ini 5, the output goes as mentioned below:
   {
  "prices": [
    {
      "average_price": "1154.6666666666666667",
      "day": "2016-01-01"
    },
    {
      "average_price": "1154.6666666666666667",
      "day": "2016-01-02"
    }
  ]
} 
