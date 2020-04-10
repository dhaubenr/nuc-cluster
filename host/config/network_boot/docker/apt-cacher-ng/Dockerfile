FROM ubuntu

VOLUME ["/var/cache/apt-cacher-ng"]
RUN apt-get update && apt-get install -y apt-cacher-ng
RUN echo "PassThroughPattern: .*" >> /etc/apt-cacher-ng/acng.conf

EXPOSE 3142
CMD chmod 777 /var/cache/apt-cacher-ng && /etc/init.d/apt-cacher-ng start && tail -f /var/log/apt-cacher-ng/*
