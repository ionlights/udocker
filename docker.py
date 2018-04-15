import os

## possible base images for the Dockerfiles
_base = {}


## accepted Dockerfiles
accepted = ["udocker/{}.Dockerfile".format(f) for f in _base.keys()]
template = "udocker/template.Dockerfile"


################################################################################
## Docker tagging and arguments
################################################################################

## docker image construction, host/image:tag
hst = ""
img = ""
tag = None  ## should be unset, is based on user spec'd args
container = None

## build arguments
args_build = [
]

## runtime arguments
PORT = 24036
args_start = [
"-v $(pwd):/{}".format(img),					## mount nanodegree
"-v $(pwd)/udocker/.jupyter:/root/.jupyter",	## mount custom jupyter configs
"-p {}:8888".format(PORT),						## jupyter->localhost port
]


def _container(use_gpu):
	tag = "gpu" if use_gpu else "cpu"
	container = "{}/{}:{}".format(hst, img, tag)


def start(use_gpu, attach=True):
	_container(use_gpu)
	default_args = [
		"--runtime=nvidia" if use_gpu else "", 	## runtime
		"--rm", 								## remove on stop
		"-d" if not attach else "",				## run container in detached _mode
		"--name {}".format(img), 				## name container for simpler management
	]

	return " ".join(
		["docker", "run"]
		+ args_default
		+ args_start
		+ [container]
	)


def build(use_gpu):
	_container(use_gpu)

	dockerfile = "udocker/{}.Dockerfile".format(tag)
	assert dockerfile in accepted

	default_args = [
		"-t {}".format(container),	## tag the container
		"-f {}".format(dockerfile),	## dockerfile
	]

	if dockerfile not in os.listdir(os.getcwd()):
		os.chdir("udocker")
		with open(template, "r") as tmpl, open(dockerfile, "w") as outp:
			outp.write(tmpl.read().replace("%%base%%", _base[tag]))

	return " ".join(
		["docker", "build", "--no-cache"]
		+ args_default
		+ args_build
		+ ["udocker"]
	)

