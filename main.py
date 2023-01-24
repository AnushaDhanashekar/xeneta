# Previous imports remain...
from time import strftime

from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func, create_engine
from datetime import datetime
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:ratestask@192.168.99.100:5432/postgres"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
engine = create_engine("postgresql://postgres:ratestask@192.168.99.100:5432/postgres")
connection = engine.connect()


# ORM model for table Ports
class Ports(db.Model):
    code = db.Column(db.String, primary_key=True)
    name = db.Column(db.String())
    parent_slug = db.Column(db.String())
    regions = db.relationship('Regions', backref='ports')
    pricess = db.relationship('Prices', backref='Prices.dest_code', primaryjoin='Ports.code==Prices.orig_code',
                              lazy='dynamic')


# ORM model for table Prices
class Prices(db.Model):
    orig_code = db.Column(db.String, db.ForeignKey('ports.code'), primary_key=True)
    dest_code = db.Column(db.String, db.ForeignKey('ports.code'), primary_key=True)
    orig = db.relationship('Ports', foreign_keys='Prices.orig_code')
    dest = db.relationship('Ports', foreign_keys='Prices.dest_code')
    day = db.Column(db.Date)
    price = db.Column(db.Integer)


# ORM model for table Regions
class Regions(db.Model):
    slug = db.Column(db.String, db.ForeignKey('ports.parent_slug'), primary_key=True)
    name = db.Column(db.String())

    parent_slug = db.Column(db.String, db.ForeignKey('regions.slug'))


# GET API individual daily prices between ports, in USD.
@app.route('/rates', methods=['POST', 'GET'])
def rates():
    # Get request param fromURL
    if request.method == 'GET':
        args = request.args
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        origin = args.get('origin')
        destination = args.get('destination')

        # Input parameters are not None and not empty
        if basicValidation(date_from, date_to, origin, destination):
            return "<h1>Some inputs are not valid</h1>"

        # Input FROM and TO dates are in valid format
        if basicDateTimeValidation(date_from, date_to):
            return "<h1>Datetime format is not valid</h1>"

        # Get actual DESTINATION when PORT CODE or SLUG is sent as part of request.get
        source = getOriginDestination(origin)
        if source is None:
            return "<h1>Invalid Source Port</h1>"

        # Get actual SOURCE when PORT CODE or SLUG is sent as part of request.get
        dest = getOriginDestination(destination)
        if dest is None:
            return "<h1>Invalid Destination Port</h1>"

        """SELECT day, AVG(price) FROM public.prices where orig_code in ('CNSGH') and dest_code in ('BEANR','BEZEE','DEBRV','DEHAM','FRLEH','NLRTM')
            and day>='2016-01-01' and day<'2016-01-10' group by day having count(day)>=3;"""
        # Main query where actual fetch to display data is written
        prices = connection.execute(
            f"SELECT {Prices.day}, {func.count(Prices.day).label('Count_of_Days')}, {func.avg(Prices.price).label('average_price')} FROM Prices WHERE Prices.orig_code in {source} and Prices.dest_code in {dest} and Prices.day between '{date_from}' and '{date_to}'  group by {Prices.day} order by {Prices.day}").fetchall()

        # prices = db.session.query(Prices.day, func.count(Prices.day).label("Count_of_Days"), func.avg(Prices.price).label("average_price")).filter(date_from <= Prices.day <= date_to and Prices.orig_code in source and Prices.dest_code in dest).group_by(Prices.day).order_by(Prices.day)
        # having(func.count(Prices.day)>=3)

        results = []
        # Format json output from resultset
        for price in prices:
            result = {}
            if price[1] < 3:
                result['average_price'] = None
            else:
                result['average_price'] = price[2]
            result['day'] = price[0].strftime("%Y-%m-%d")
            results.append(result)
        return {"prices": results}
    else:
        return "<h1>Only GET Requests are Allowed</h1>"


def basicValidation(date_from, date_to, origin, destination):
    if date_from is None or date_to is None or origin is None or destination is None or date_from is "" or date_to is "" or origin is "" or destination is "":
        return True
    else:
        return False


def basicDateTimeValidation(date_from, date_to):
    try:
        if datetime.strptime(date_from, "%Y-%m-%d") and datetime.strptime(date_to, "%Y-%m-%d") and date_from <= date_to:
            return False
        else:
            return True
    except ValueError:
        return True


def getOriginDestination(portCode):
    if portCode is "" or portCode is None: return None

    # When ORIGIN or DESTINATION is Port CODE
    source = connection.execute(f"SELECT {Ports.code} FROM Ports WHERE {Ports.code} = '{portCode}'").fetchall()
    if len(source) > 0:
        return getArrayOutOfResultSet(source)

    # When ORIGIN or DESTINATION is Parent Slug
    source = connection.execute(
        f"SELECT {Regions.parent_slug} FROM Regions WHERE {Regions.parent_slug} = '{portCode}'").fetchall()
    if len(source) > 0:
        source = connection.execute(
            f"SELECT {Ports.code} FROM Ports WHERE {Ports.parent_slug} in (SELECT {Regions.slug} FROM Regions WHERE {Regions.parent_slug} = '{portCode}')").fetchall()
        return getArrayOutOfResultSet(source)

    # When ORIGIN or DESTINATION is Slug
    source = connection.execute(
        f"SELECT {Regions.slug} FROM Regions WHERE {Regions.parent_slug} = '{portCode}'").fetchall()
    if len(source) > 0:
        source = connection.execute(
            f"SELECT {Ports.code} FROM Ports WHERE {Ports.parent_slug} in (SELECT {Regions.slug} FROM Regions WHERE {Regions.parent_slug} = '{portCode}')").fetchall()
        return getArrayOutOfResultSet(source)
    else:
        return None


def getArrayOutOfResultSet(resultset):
    result = [r for r, in resultset]
    ','.join(f"'{x}'" for x in result)
    print(str(result).replace('[', '(').replace(']', ')'))
    return str(result).replace('[', '(').replace(']', ')')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
