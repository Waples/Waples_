# $(whoami)

My code for launching / updating my personal website on AWS S3 static hosting.

I created some modules and a wrapper based around the AWS `boto3` library to automatically create my static website on my AWS account.

Please see [labs.py](labs/labs.py)


## Current look... (I know it sucks).
![current](current.png)


### ToDo
- [ ] Rebuild with a yaml or json file.
- [ ] Add my yaml-json-yaml converter module.
- [ ] Add my static website generator `genny`.
- [ ] Convert genny to a package.
- [ ] Allot more....


##### Headsup
Remember to set the correct `AWS_PROFILE` env value before running `labs.py`.
