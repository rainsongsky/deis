#!/usr/bin/env bash

if [ -z $1 ]; then
  echo usage: $0 [region]
  exit 1
fi

region=$1

# TODO: prepare an optimized snapshot for this account
# as we do for EC2 AMIs


# rackspace settings
flavor="4"
image="23b564c9-c3e6-49f9-bc68-86c7a9ab5018"

# ssh settings
# ssh_key_path=~/.ssh/$key_name
ssh_user="root"

# chef settings
node_name="deis-controller"
run_list="recipe[deis::controller]"
chef_version=11.4.4

function echo_color {
  echo -e "\033[1m$1\033[0m"
}

# # create security group and authorize ingress
# if ! ec2-describe-group | grep -q "$sg_name"; then
#   echo_color "Creating security group: $sg_name"
#   set -x
#   ec2-create-group $sg_name -d "Created by Deis"
#   set +x
#   echo_color "Authorizing TCP ports 22,80,443,514 from $sg_src..."
#   set -x
#   ec2-authorize deis-controller -P tcp -p 22 -s $sg_src >/dev/null
#   ec2-authorize deis-controller -P tcp -p 80 -s $sg_src >/dev/null
#   ec2-authorize deis-controller -P tcp -p 443 -s $sg_src >/dev/null
#   ec2-authorize deis-controller -P tcp -p 514 -s $sg_src >/dev/null
#   set +x
# else
#   echo_color "Security group $sg_name exists"
# fi

# # create ssh keypair and store it
# if ! test -e $ssh_key_path; then
#   echo_color "Creating new SSH key: $key_name"
#   set -x
#   ec2-create-keypair $key_name > $ssh_key_path
#   chmod 600 $ssh_key_path
#   set +x
#   echo "Saved to $ssh_key_path"
# else
#   echo_color "SSH key $ssh_key_path exists"
# fi

# create data bags
knife data bag create deis-build 2>/dev/null
knife data bag create deis-formations 2>/dev/null

# create data bag item using a temp file
tempfile=$(mktemp -t tmp.deisXXXXXXXXXX)
mv $tempfile $tempfile.json
cat > $tempfile.json <<EOF
{ "id": "gitosis", "ssh_keys": {}, "formations": {} }
EOF
knife data bag from file deis-build $tempfile.json
rm -f $tempfile.json

# trigger rackspace instance bootstrap
echo_color "Provisioning $node_name with rumm..."
set -x
rumm create server --name $node_name --image-id $image --flavor_id $flavor

rumm ssh $node_name
knife
# knife ec2 server create \
#  --bootstrap-version $chef_version \
#  --region $region \
#  --image $image \
#  --flavor $flavor \
#  --groups $sg_name \
#  --tags Name=$node_name \
#  --ssh-key $key_name \
#  --ssh-user $ssh_user \
#  --identity-file $ssh_key_path \
#  --node-name $node_name \
#  --ebs-size $ebs_size \
#  --run-list $run_list
# set +x
