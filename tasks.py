from invoke import task
import yaml

project_name = "test-dynamo"


@task
def ci_tests(context):
    setup_test(context)
    try:
        unit_tests(context)
    finally:
        tear_down_test(context)


@task
def setup_test(context):
    tear_down_test(context)
    context.run("docker-compose up -d")


@task
def tear_down_test(context):
    context.run("docker-compose down")


@task
def unit_tests(context):
    context.run("sbt test")


@task
def docker_test_and_dist(context):
    
    context.run('rm -rf test_reports')
    context.run('rm -rf docker_output')
    
    context.run("docker-compose up -d")
    context.run('docker build -f test_Dockerfile -t radioactive/'+project_name+'_test:latest .')
    context.run('docker-compose  -f docker-compose.yml -f docker-compose.test.yml run test_and_publish')

    container_id = context.run(" docker ps -a --filter ancestor=radioactive/"+project_name+"_test -l -q").stdout.strip()
    context.run('docker cp ' + container_id + ':/code/target/test-reports test_reports')
    context.run('docker cp ' + container_id + ':/code/target/universal docker_output ')


@task
def docker_build(context,tag):
    img = 'radioactive/'+project_name + ':' + tag
    context.run('rm -rf docker_build')
    context.run('mkdir docker_build')
    context.run('cp production_Dockerfile docker_build/Dockerfile')
    context.run('unzip docker_output/'+project_name+'-SNAPSHOT.zip -d docker_build')
    with context.cd("docker_build"):
        context.run("docker build -t " + img + " .")


@task
def docker_publish(context,tag):
    imgname = 'radioactive/%s:%s' % (project_name, tag)
    reponame = '%s/%s:%s' % (repo, project_name, tag)
    context.run('docker tag %s %s' % (imgname, reponame))
    context.run('docker push %s' % reponame)
    artifact_metadata = {"docker": {"image": reponame}}
    context.run('rm -rf release_candidate')
    context.run('mkdir release_candidate')
    with open('release_candidate/metadata.yml', 'w') as outfile:
        yaml.dump(artifact_metadata, outfile, default_flow_style=False)


@task
def docker_build_and_publish(context):
    tag = get_tag(context)
    docker_build(context,tag)
    docker_publish(context,tag)


@task
def get_tag(context):
    short_commit_id = context.run("git log --pretty=format:'%h' -n 1" , hide=True).stdout.strip()
    date = context.run("date +%F", hide=True).stdout.strip()
    return str(date) + "_" + str(short_commit_id)
