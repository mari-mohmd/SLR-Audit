# Generates a bytecode for local_scope.py and global_scope.py.
Echo "Generating bytecode for local_scope.py"
python3.9 -m dis local_scope.py
echo "--------------------------------"
echo "Generating bytecode for global_scope.py"
python3.9 -m dis global_scope.py
