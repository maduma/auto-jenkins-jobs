VERSION=0.3.1
docker build --build-arg AUTOJJ_VERSION=$VERSION -t registry.in.luxair.lu/infra/autojj:$VERSION .
