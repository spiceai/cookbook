FROM debian AS build

RUN apt-get update && apt-get install -yqq curl ca-certificates

# Rebuild when a new runtime release is published.
ADD "https://api.github.com/repos/spiceai/spiceai/releases/latest" latest_release

# Release assets are named spiced_linux_<arch>.tar.gz.
RUN set -eux; \
    case "$(uname -m)" in \
      aarch64|arm64) arch=aarch64 ;; \
      x86_64|amd64) arch=x86_64 ;; \
      *) echo "unsupported architecture: $(uname -m)" >&2; exit 1 ;; \
    esac; \
    tag="$(sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' latest_release | head -n 1)"; \
    test -n "$tag"; \
    curl -fL "https://github.com/spiceai/spiceai/releases/download/${tag}/spiced_linux_${arch}.tar.gz" \
      | tar -xz -C /usr/local/bin spiced; \
    chmod a+x /usr/local/bin/spiced

FROM debian

RUN apt-get update && apt-get install -yqq libssl-dev ca-certificates

COPY --from=build /usr/local/bin/spiced /usr/local/bin

WORKDIR /root

ENTRYPOINT ["spiced", "--flight", "0.0.0.0:50051"]