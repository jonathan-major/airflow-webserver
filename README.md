Airflow-Webserver
--------------------------------------------------------------

UPDATE: I've created a [Pull Request](https://github.com/apache/incubator-airflow/pull/3015) against [Apache-Airflow](https://github.com/apache/incubator-airflow) master (review/testing welcome!). It will be released with Airflow 1.10. In order to introduce RBAC feature to Airflow sooner, the DAG-level permission feature is deprioritized for a future release. 

Airflow Webserver uses the [Flask-AppBuilder (FAB)](https://github.com/dpgaspar/Flask-AppBuilder) extension instead of Flask-Admin. The goal of this Airflow Webserver is to leverage FAB's build-in security features to introduce the following capabilities in the UI:
- role-based access control
- support for various authentications backends (OAuth, OpenID, Database, LDAP, etc.)
- dag-level permissions

Airflow-Webserver will be merged back into Airflow's source code in the near future. Contributions are welcome!

Setup
--------------------------------------------------------------

Airflow-Webserver is written on top of Airflow 1.9.0, which is not currently in PyPI. Make sure you have airflow 1.9.0+ installed before attempting the setup below.

- Clone the repo

        `git clone git@github.com:wepay/airflow-webserver.git`
        `cd airflow-webserver`

- Install Flask-AppBuilder

        `pip install flask-appbuilder`

- To set up the database object, modify the SQLALCHEMY_DATABASE_URI variable in `config.py` to your Airflow db.
  Note this will generate new tables which FAB uses for its security model.
  
        `fabmanager create-db --app airflow_webserver`

- To create an admin account

        `fabmanager create-admin --app airflow_webserver`

- To start the webserver

        `fabmanager run --app airflow_webserver`
