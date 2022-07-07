PYPI_USERNAME="yinzheng-zhong"

rm -r build dist tfgen.egg-info

python setup.py sdist bdist_wheel
# check if twine is installed
if [ -z "$(which twine)" ]; then
    echo "Please install twine first then run this shell again: pip install twine"
    read -rp "Press [Enter] to quit"
fi

CHECK_OUTPUT=$(twine check dist/*)

# check if FAILED is present in the $CHECK_OUTPUT
if [[ $CHECK_OUTPUT == *"FAILED"* ]]; then
    echo "!!twine check FAILED!!"
    echo "${CHECK_OUTPUT}"
    read -rp "Press [Enter] to quit"
else
    echo "----------------------------------------------------------"
    echo "Uploading to PyPI..."
    echo "Enter password"
    read -rsp "Password: " PASSWORD

    twine upload --username "$PYPI_USERNAME" --password "$PASSWORD" dist/*
fi
