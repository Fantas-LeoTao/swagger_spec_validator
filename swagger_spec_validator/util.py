import logging
import yaml
import json
import click

from swagger_spec_validator import validator12, validator20
from swagger_spec_validator.common import SwaggerValidationError
from swagger_spec_validator.common import load_json
from swagger_spec_validator.common import wrap_exception


log = logging.getLogger(__name__)


def get_validator(spec_json, origin='unknown'):
    """
    :param spec_json: Dict representation of the json API spec
    :param origin: filename or url of the spec - only use for error messages
    :return: module responsible for validation based on Swagger version in the
        spec
    """
    swagger12_version = spec_json.get('swaggerVersion')
    swagger20_version = spec_json.get('swagger')

    if swagger12_version and swagger20_version:
        raise SwaggerValidationError(
            "You've got conflicting keys for the Swagger version in your spec. "
            "Expected `swaggerVersion` or `swagger`, but not both.")
    elif swagger12_version and swagger12_version == '1.2':
        # we don't care about versions prior to 1.2
        return validator12
    elif swagger20_version and swagger20_version == '2.0':
        return validator20
    elif swagger12_version is None and swagger20_version is None:
        raise SwaggerValidationError(
            "Swagger spec {0} missing version. Expected "
            "`swaggerVersion` or `swagger`".format(origin))
    else:
        raise SwaggerValidationError(
            'Swagger version {0} not supported.'.format(
                swagger12_version or swagger20_version))


@wrap_exception
def validate_spec_url(spec_url):
    """Validates a Swagger spec given its URL.

    :param spec_url:
      For Swagger 1.2, this is the URL to the resource listing in api-docs.
      For Swagger 2.0, this is the URL to swagger.json in api-docs. If given
                       as `file://` this must be an absolute url for
                       cross-refs to work correctly.
    """
    spec_json = load_json(spec_url)
    validator = get_validator(spec_json, spec_url)
    validator.validate_spec(spec_json, spec_url)


@click.command()
@click.argument('spec_file')
@wrap_exception
def validate_spec(spec_file):
    click.echo('swagger validate start!')
    with open(spec_file) as f:
        if spec_file.endswith('.yml') or spec_file.endswith('.yaml'):
            spec_json = yaml.load(f)
        elif spec_file.endswith('.json'):
            spec_json = json.load(f)
        else:
            click.echo('swagger file neither json nor yaml')
            return

    validator = get_validator(spec_json)
    validator.validate_spec(spec_json)
    click.echo('swagger validate finished!')
