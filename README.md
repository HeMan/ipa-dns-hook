# FreeIPA hook for `dehydrated`

This is a hook for the [Let's Encrypt](https://letsencrypt.org/) ACME client [dehydrated](https://github.com/lukas2511/dehydrated) (previously known as `letsencrypt.sh`) that allows you to use DNS records in a FreeIPA to respond to `dns-01` challenges. Requires Python, requests and requests-kerberos.

## Installation

```
$ git clone https://github.com/lukas2511/dehydrated
$ cd dehydrated
$ mkdir hooks
$ git clone https://github.com/HeMan/ipa-dns-hook.git hooks/ipa-dns
$ pip install -r hooks/ipa-dns/requirements.txt
```

## Configuration
Your IPA-server and domain is expected to be in the environment.

```
export IPA_SERVER=myipa.example.com
export IPA_DOMAIN=example.com
```

It uses Kerberos authentication by default. To use username and password you need to set environment variables IPA_USER and IPA_PASSWORD.
```
export IPA_USER=admin
export IPA_PASSWORD=s3cretp4ssword
```

These could also be placed in `dehydrated/config`, which is read by dehydrated.


```
echo "export IPA_SERVER=myipa.example.com" >> dehydrated/config
echo "export IPA_DOMAIN=example.com" >> dehydrated/config
echo "export IPA_USER=admin" >> dehydrated/config
echo "export IPA_PASSWORD=s3cretp4ssword" >> dehydrated/config
```


## Usage
```
$ ./dehydrated -k hooks/ipa-dns/ipa-dns-hook.py -t dns-01 -c --accept-terms -d myhost.example.com

# !! WARNING !! No main config file found, using default config!
#
Processing myhost.example.com
 + Signing domains...
 + Creating new directory /home/user/dehydrated/certs/myhost.example.com ...
 + Generating private key...
 + Generating signing request...
 + Requesting challenge for myhost.example.com...
 + freeipa hook executing: deploy_challenge
 + Responding to challenge for myhost.example.com...
 + freeipa hook executing: clean_challenge
 + Challenge is valid!
 + Requesting certificate...
 + Checking certificate...
 + Done!
 + Creating fullchain.pem...
 + Using cached chain!
 + freeipa hook executing: deploy_cert
 + Done!

```

