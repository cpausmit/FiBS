# generate the setup file
rm -f setup.sh
touch setup.sh

# first the base directory and the path
echo "# CAREFUL THIS FILE IS GENERATED AT INSTALL"                  >> setup.sh
echo "export FIBS_BASE=`pwd`"                                       >> setup.sh
echo "export FIBS_CFGS=\$FIBS_BASE/config"                          >> setup.sh
echo "export FIBS_TASK=\$FiBS_BASE/task"                            >> setup.sh

echo "export FIBS_WORK=\$HOME/work/fibs"                            >> setup.sh
echo "export FIBS_LOGS=\$HOME/logs/fibs"                            >> setup.sh
echo "export FIBS_DEBUG=0"                                          >> setup.sh
echo "export PATH=\${PATH}:\${FIBS_BASE}/bin"                       >> setup.sh
echo "export PYTHONPATH=\${PYTHONPATH}:\${FIBS_BASE}/python"        >> setup.sh
