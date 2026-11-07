TABLEAU DREMIO DRIVER
=====================

The workbook Tableau_Churn_Dashboard.twb connects to the demo Dremio
server through the Dremio JDBC driver. Tableau Desktop does not ship
that driver, so install it once on the presentation machine:

1. Install Tableau Desktop (the free edition is enough; publishing is
   not used).
2. Copy dremio-jdbc-driver-26.0.5.jar from this folder into:
   C:\Users\<you>\Documents\My Tableau Repository\Drivers
3. Restart Tableau Desktop if it was already open.
4. Open Tableau_Churn_Dashboard.twb in the main project folder.
5. Enter the Dremio admin password when Tableau asks (username admin).
   The Dremio server must be running on localhost:31010 first.

The jar is the same Dremio JDBC driver (26.0.5) used to build and
verify the workbook. If the file is ever missing, download the matching
Dremio JDBC driver and use the same Drivers folder.
