import sys
import getopt
import psycopg2

from time_logger import TimeLogger
from psycopg2.extras import NamedTupleCursor

# flags that will be used as input params
flag_options = 'H:D:S:'
# values corresponding to the flag options
menu_options = ['host=', 'dbname=', 'support']

class Main:
    
    def __init__(self, argv) -> None:
        """Constructor
        Accept input arguments to method and initialize host, dbname, default min_support and options
        Args:
            argv (List): List of input strings as arguments to the program
        """
        self.host = None
        self.dbname = None
        self.min_support = 5
        self.timer = TimeLogger()
        self.options, _ = getopt.getopt(argv[1:], flag_options, menu_options)
        if not self.options:
            sys.exit(1)
        self._handle_input_args()
    
    def _handle_input_args(self) -> None:
        """Extract values based on the input given to the program
        """
        for option, arg in self.options:
            if option in ('-H', '--hostname'):
                self.host = arg
            elif option in ('-D', '--dbname'):
                self.dbname = arg
            elif option in ('-S', '--support'):
                self.min_support = int(arg)
            else:
                sys.exit(1)
        
    def _establish_connection(self) -> None:
        """Establish postgresql db connection based on the input hostname and database name
        """
        try:
            connection = psycopg2.connect(host=self.host, dbname=self.dbname)
            connection.set_session(autocommit=True)
            self.cursor = connection.cursor(cursor_factory=NamedTupleCursor)
        except (psycopg2.OperationalError) as connection_error:
            print(connection_error)
            print('Exiting program ...')
            sys.exit(1)

    def _generate_select_clause(self, iterations: int) -> str:
        """Generate select clause of the SQL query for creating the itemset tables
        Args:
            iterations (int): Integer value representing the number of itemset pairs to be included in the table
        Returns:
            str: String representing the select clause
        """
        attributes = "t1.artist_id as artist_1"
        for index in range(2, iterations+1):
            attributes += f", t{index}.artist_id as artist_{index}"
        return f"{attributes}, COUNT(1) "

    def _generate_join_clause(self, iterations: int) -> str:
        """Generate join clause of the SQL query for creating the itemset tables
        Args:
            iterations (int): Integer value representing the number of itemset pairs to be included in the table
        Returns:
            str: String representing the join clause
        """
        join_clause = "album_artist as t1 "
        for index in range(2, iterations+1):
            join_clause += f"JOIN album_artist as t{index} ON t{index-1}.album_id = t{index}.album_id "
        return join_clause
    
    def _generate_lattice_join_clause(self, iterations: int) -> str:
        join_clause = f"JOIN L{iterations-1} ON "
        for index in range(1, iterations):
            if index < iterations - 1:
                join_clause += f"t{index}.artist_id = L{iterations-1}.artist_{index} AND "
            elif index == iterations - 1:
                join_clause += f"t{index}.artist_id = L{iterations-1}.artist_{index} "
        return join_clause

    
    def _generate_where_clause(self, iterations: int) -> str:
        """Generate where clause of the SQL query for creating the itemset tables
        Args:
            iterations (int): Integer value representing the number of itemset pairs to be included in the table
        Returns:
            str: String representing the where clause
        """
        where_clause = f" t{iterations-1}.artist_id < t{iterations}.artist_id "
        return where_clause
    
    def _generate_group_by_clause(self, iterations: int) -> str:
        """Generate the group by clause of the SQL query for creating the itemset tables
        Args:
            iterations (int): Integer value representing the number of itemset pairs to be included in the table
        Returns:
            str: String representing the group by clause
        """
        group_by_clause = "(t1.artist_id"
        for index in range(2, iterations+1):
            group_by_clause += f", t{index}.artist_id"
        group_by_clause += ')'
        return group_by_clause
    
    def _execute_final_query(self, iterations: int):
        """Take the last created itemset table and join with Member table to fetch the name of the actors in the itemset
        table
        Args:
            iterations (int): Integer value representing the number of itemset pairs in the final table 
        """
        select_query = "SELECT "
        join_query = ""
        for index in range(1, iterations+1):
            if index < iterations:
                select_query += f"m{index}.name as artist_{index}, "
            elif index == iterations:
                select_query += f"m{index}.name as artist_{index}"
            join_query += f" JOIN artist m{index} on L{iterations}.artist_{index} = m{index}.id"
        query = f"{select_query}, count as collabs FROM L{iterations} {join_query}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        for row in result:
            print(row)
        
    
    def _build_query(self, iterations: int) -> str:
        """Builds and returns the query
        Args:
            iterations (int): Number of iterations
        Returns:
            str: String value of the query that needs to be run
        """
        return (f"SELECT {self._generate_select_clause(iterations)} INTO L{iterations} "
                f"FROM {self._generate_join_clause(iterations)}"
                f"{self._generate_lattice_join_clause(iterations)}"
                f"WHERE {self._generate_where_clause(iterations)}"
                f"GROUP BY {self._generate_group_by_clause(iterations)} " 
                f"HAVING COUNT(1) >= {self.min_support}")
        
    def _build_l1(self) -> None:
        self.cursor.execute("DROP TABLE IF EXISTS L1")
        return (f"SELECT artist_id as artist_1, count(1) INTO L1 "
        f"FROM album_artist GROUP BY artist_id "
        f"HAVING count(1) >= {self.min_support}; ")

    def _create_lattices(self) -> int:
        """Creates lattices iteratively until the last table is created with 0 rows
        Returns:
            int: the last value of iteration that produced records
        """
        iterations = 1
        while True:
            iterations += 1
            self.cursor.execute(f"DROP TABLE IF EXISTS L{iterations}")
            query = self._build_query(iterations)
            self.cursor.execute(query)
            self.cursor.execute(f"SELECT COUNT(1) FROM L{iterations}")
            result = self.cursor.fetchone()
            # if the table has 0 rows then that it the end of the loop as no more combinations exist
            if result.count == 0:
                # drop the table that has 0 rows
                print(f"Created table: L{iterations}; Number of rows = {result.count}") 
                print(f"Dropping table L{iterations}..")
                self.cursor.execute(f"DROP TABLE L{iterations}")
                # break out of loop
                break
            last_iteration = iterations
            print(f"Created table: L{iterations}; Number of rows = {result.count}") 
        return last_iteration
    
    def _execute_itemset_mining(self) -> None:
        """Public method that is called to execute the program.
        Create all itemset tables until the one with 0 rows is encountered.
        Delete the table with 0 rows
        Fetch the names of the actors as part of the final itemset table
        """
        print("Commencing Itemset Mining ...\n")
        self.timer.start()
        # iterations = 1
        self.cursor.execute(self._build_l1())
        last_iteration = self._create_lattices()
        print(f"Last created table with records = L{last_iteration}")
        self._execute_final_query(last_iteration)
        print("Itemset Mining complete ...")
        self.timer.end()

    def _clean_database(self) -> None:
        """Performs Data cleaning
        """
        self.timer.start()
        print("Commencing Database Cleaning ...")
        self.cursor.execute(open('sql_scripts/integrity_checks.sql').read())
        self.cursor.execute(open('sql_scripts/removals.sql').read())
        print("Data cleaning complete...")
        self.timer.end()
    
    def execute(self) -> None:
        """Entry point to the program
        """
        self._establish_connection()
        option = int(input("Enter 1 for cleaning data or 2 for itemset mining: "))
        if option == 1:
            self._clean_database()
        elif option == 2:
            self._execute_itemset_mining()
        else:
            print("Invlalid input")
            sys.exit(1)

if __name__ == '__main__':
    Main(sys.argv).execute()