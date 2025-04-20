from fastapi import HTTPException, status

def bad_request_exception(detail="Malformed request"):
  return HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=detail,
      headers={"WWW-Authenticate": "Bearer"},
  )

def auth_exception(detail="Could not validate credentials",headers=None):
  return HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail=detail,
      headers=headers if headers else {"WWW-Authenticate": "Bearer"},
  )

def forbidden_exception(detail="You do not have permission to access this resource"):
  return HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=detail
  )

def not_found_exception(detail="Item not found"):
  return HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=detail
  )

def teapot_exception(detail="I'm just a teapot"):
  return HTTPException(
      status_code=status.HTTP_418_IM_A_TEAPOT,
      detail=detail
  )

def too_many_requests_exception(detail="Too many requests, try again later"):
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail
    )

def internal_server_exception(detail="Internal server error"):
  return HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=detail
  )

def service_unavailable_exception(detail="Service unavailable, please try again later"):
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail
    )
