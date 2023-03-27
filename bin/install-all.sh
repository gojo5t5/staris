BIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

pushd $BIN_DIR

# for s in conjure savilerow mininzinc irace runsolver ortools yuck picat
for s in mininzinc ortools yuck picat
do
    bash install-${s}.sh
done

sudo apt-get install powertop

git clone https://github.com/powerapi-ng/jouleit.git
pushd jouleit
mv jouleit.sh ../
popd jouleit
rm -rf jouleit
popd
