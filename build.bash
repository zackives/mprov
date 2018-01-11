#!/bin/bash

SWAGGER_BIN="./bin"
OUTPUT_DIR="pennprov_python_client"
PACKAGE="pennprov"

echo "removing existing ${OUTPUT_DIR} (if any)"
rm -fr ${OUTPUT_DIR}

${SWAGGER_BIN}/swagger-codegen generate \
  -i spec/swagger.yaml \
  -l python \
  --additional-properties packageName=${PACKAGE} \
  -o ${OUTPUT_DIR}
