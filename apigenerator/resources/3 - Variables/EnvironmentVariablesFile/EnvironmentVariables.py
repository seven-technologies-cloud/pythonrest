# System Imports #
import os

# ------------------------------------------ Database ------------------------------------------ #

# Database start configuration #

# Configuration for database connection #


# ------------------------------------------ Domain ------------------------------------------ #

# UID Generation Type #

# Filter generation environment variables #
os.environ['domain_like_left'] = ''
os.environ['domain_like_right'] = ''
os.environ['domain_like_full'] = ''

# Datetime valid masks #
os.environ['date_valid_masks'] = "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y"
os.environ['time_valid_masks'] = "%H:%M:%S, %I:%M:%S %p, %H:%M, %I:%M %p, %I:%M:%S%p, %I:%M%p, %H:%M:%S%z, %I:%M:%S %p%z, %H:%M%z, %I:%M %p%z, %I:%M:%S%p%z, %I:%M%p%z, %H:%M:%S.%f, %I:%M:%S.%f %p, %H:%M:%S.%f%z, %I:%M:%S.%f %p%z, %H:%M:%S.%fZ, %I:%M:%S.%f %pZ, %H:%M:%S.%f %Z, %I:%M:%S.%f %p %Z"

os.environ['query_limit'] = '*'

# --------------------------------------- API Behavior --------------------------------------- #

# Batch Insert Strategy #
# Defines the strategy for handling batch insert operations (e.g., via POST to a collection endpoint).
# Possible values:
#   'ITERATIVE': (Default) Uses an iterative approach (session.add() per item) within a single transaction.
#                This strategy allows for more granular error reporting if some items in a batch
#                fail due to database constraints (e.g., duplicate keys), while others might succeed.
#                The transaction will commit successfully processed items if any, and report errors for failed ones.
#   'BULK':      Uses session.execute(insert(), data_list) for potentially higher performance on very large batches.
#                Database errors (like duplicate keys or other constraint violations) will likely cause
#                the entire batch operation to fail (all-or-nothing transaction behavior for the batch).
#                Error reporting will be for the batch as a whole, not per item.
os.environ.setdefault('API_BATCH_INSERT_STRATEGY', 'ITERATIVE')


# ------------------------------------------ Trace ------------------------------------------ #

# Comment this variable bellow for NO STACKTRACE (production mode off) #
os.environ['display_stacktrace_on_error'] = 'False'

# ------------------------------------------ Origins ------------------------------------------ #

# Origins enabled #
os.environ['origins'] = '*'
os.environ['headers'] = '*'
