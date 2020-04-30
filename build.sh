VERSION=v0.2.4
docker build --build-arg AUTOJJ_VERSION=$VERSION -t registry.in.luxair.lu/infra/autojj:$VERSION .
