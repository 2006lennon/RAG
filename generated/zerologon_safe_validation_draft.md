# Zerologon Safe Validation Draft

## Question

Why is AES-CFB8 relevant to Zerologon?

## Retrieved Context

### Context 1
Source: ms_nrpc_notes.txt
Chunk: 0

Microsoft Netlogon Remote Protocol (MS-NRPC) Notes
==================================================

Purpose
-------
MS-NRPC is a Microsoft RPC protocol used by Windows domain members
and domain controllers for authentication-related operations.

Zerologon
---------
CVE-2020-1472, also known as Zerologon, is a vulnerability in the
Netlogon Remote Protocol.

The vulnerability is related to the cryptographic design used during
the Netlogon authentication process.

The issue involved the use of AES-CFB8 with a zero initialization
vector and specially crafted values that could cause authentication
to succeed with a small probability.


### Context 2
Source: ms_nrpc_notes.txt
Chunk: 1

Repeated attempts could therefore eventually result in a successful
authentication attempt.

Important Concepts
------------------

1. Netlogon
   Netlogon provides secure communication between Windows domain
   members and domain controllers.

2. Secure Channel
   A secure channel is normally established between a machine account
   and the domain controller.

3. Challenge-Response
   The client and server exchange challenge values during
   authentication.

4. Credential
   Authentication credentials are computed based on shared secrets
   and cryptographic operations.

5. AES-CFB8
   Zerologon is associated with the use of AES in CFB8 mode.

6. Initialization Vector

### Context 3
Source: impacket_api.txt
Chunk: 0

Impacket NRPC API Reference Notes
=================================

Purpose
-------
Impacket is a Python library that implements several network protocols.

For this project, Impacket documentation is treated only as static
reference material.

No Impacket module is imported or executed by the RAG program.

Relevant Module
---------------
impacket.dcerpc.v5.nrpc

The nrpc module contains structures and functions related to the
Microsoft Netlogon Remote Protocol.

Example API Names
-----------------

NetrServerReqChallenge

Purpose:
Represents the Netlogon challenge request operation.

Conceptually, a client provides a challenge value and the server
returns its own challenge value.

