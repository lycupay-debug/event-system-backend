import type * as lark from "@larksuiteoapi/node-sdk";
import { createBitableMethods, createBitableAttachmentMethods } from "../src/resources";

const client = {} as lark.Client;
const methods = createBitableMethods(client);
const attachments = createBitableAttachmentMethods(client);

type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends
  (<T>() => T extends B ? 1 : 2)
    ? true
    : false;
type Assert<T extends true> = T;
type PayloadMatchesSdk<Wrapped extends (...args: any[]) => any, Sdk extends (...args: any[]) => any> = Equal<
  Parameters<Wrapped>[0],
  NonNullable<Parameters<Sdk>[0]>
>;

// Every public Bitable wrapper must keep the exact first-argument schema
// from its corresponding official SDK method.
type AllBitablePayloadContracts = [
  Assert<PayloadMatchesSdk<typeof methods.apps.create, typeof client.bitable.app.create>>,
  Assert<PayloadMatchesSdk<typeof methods.apps.get, typeof client.bitable.app.get>>,
  Assert<PayloadMatchesSdk<typeof methods.apps.update, typeof client.bitable.app.update>>,
  Assert<PayloadMatchesSdk<typeof methods.apps.copy, typeof client.bitable.app.copy>>,
  Assert<PayloadMatchesSdk<typeof methods.tables.create, typeof client.bitable.appTable.create>>,
  Assert<PayloadMatchesSdk<typeof methods.tables.list, typeof client.bitable.appTable.list>>,
  Assert<PayloadMatchesSdk<typeof methods.tables.update, typeof client.bitable.appTable.patch>>,
  Assert<PayloadMatchesSdk<typeof methods.tables.delete, typeof client.bitable.appTable.delete>>,
  Assert<PayloadMatchesSdk<typeof methods.tables.batchCreate, typeof client.bitable.appTable.batchCreate>>,
  Assert<PayloadMatchesSdk<typeof methods.tables.batchDelete, typeof client.bitable.appTable.batchDelete>>,
  Assert<PayloadMatchesSdk<typeof methods.records.create, typeof client.bitable.appTableRecord.create>>,
  Assert<PayloadMatchesSdk<typeof methods.records.get, typeof client.bitable.appTableRecord.get>>,
  Assert<PayloadMatchesSdk<typeof methods.records.list, typeof client.bitable.appTableRecord.list>>,
  Assert<PayloadMatchesSdk<typeof methods.records.search, typeof client.bitable.appTableRecord.search>>,
  Assert<PayloadMatchesSdk<typeof methods.records.update, typeof client.bitable.appTableRecord.update>>,
  Assert<PayloadMatchesSdk<typeof methods.records.delete, typeof client.bitable.appTableRecord.delete>>,
  Assert<PayloadMatchesSdk<typeof methods.records.batchCreate, typeof client.bitable.appTableRecord.batchCreate>>,
  Assert<PayloadMatchesSdk<typeof methods.records.batchGet, typeof client.bitable.appTableRecord.batchGet>>,
  Assert<PayloadMatchesSdk<typeof methods.records.batchUpdate, typeof client.bitable.appTableRecord.batchUpdate>>,
  Assert<PayloadMatchesSdk<typeof methods.records.batchDelete, typeof client.bitable.appTableRecord.batchDelete>>,
  Assert<PayloadMatchesSdk<typeof methods.fields.create, typeof client.bitable.appTableField.create>>,
  Assert<PayloadMatchesSdk<typeof methods.fields.list, typeof client.bitable.appTableField.list>>,
  Assert<PayloadMatchesSdk<typeof methods.fields.update, typeof client.bitable.appTableField.update>>,
  Assert<PayloadMatchesSdk<typeof methods.fields.delete, typeof client.bitable.appTableField.delete>>,
  Assert<PayloadMatchesSdk<typeof methods.views.create, typeof client.bitable.appTableView.create>>,
  Assert<PayloadMatchesSdk<typeof methods.views.get, typeof client.bitable.appTableView.get>>,
  Assert<PayloadMatchesSdk<typeof methods.views.list, typeof client.bitable.appTableView.list>>,
  Assert<PayloadMatchesSdk<typeof methods.views.update, typeof client.bitable.appTableView.patch>>,
  Assert<PayloadMatchesSdk<typeof methods.views.delete, typeof client.bitable.appTableView.delete>>,
  Assert<PayloadMatchesSdk<typeof methods.forms.get, typeof client.bitable.appTableForm.get>>,
  Assert<PayloadMatchesSdk<typeof methods.forms.update, typeof client.bitable.appTableForm.patch>>,
  Assert<PayloadMatchesSdk<typeof methods.forms.upgrade, typeof client.bitable.appTableForm.upgrade>>,
  Assert<PayloadMatchesSdk<typeof methods.forms.listFields, typeof client.bitable.appTableFormField.list>>,
  Assert<PayloadMatchesSdk<typeof methods.forms.updateField, typeof client.bitable.appTableFormField.patch>>,
  Assert<PayloadMatchesSdk<typeof methods.fieldGroups.create, typeof client.bitable.appTableFieldGroup.create>>,
  Assert<PayloadMatchesSdk<typeof methods.dashboards.list, typeof client.bitable.appDashboard.list>>,
  Assert<PayloadMatchesSdk<typeof methods.dashboards.copy, typeof client.bitable.appDashboard.copy>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.create, typeof client.bitable.appRole.create>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.list, typeof client.bitable.appRole.list>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.update, typeof client.bitable.appRole.update>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.delete, typeof client.bitable.appRole.delete>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.listMembers, typeof client.bitable.appRoleMember.list>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.createMember, typeof client.bitable.appRoleMember.create>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.batchCreateMembers, typeof client.bitable.appRoleMember.batchCreate>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.deleteMember, typeof client.bitable.appRoleMember.delete>>,
  Assert<PayloadMatchesSdk<typeof methods.roles.batchDeleteMembers, typeof client.bitable.appRoleMember.batchDelete>>,
  Assert<PayloadMatchesSdk<typeof methods.workflows.list, typeof client.bitable.appWorkflow.list>>,
  Assert<PayloadMatchesSdk<typeof methods.workflows.update, typeof client.bitable.appWorkflow.update>>,
  Assert<PayloadMatchesSdk<typeof methods.blockWorkflows.list, typeof client.bitable.appBlockWorkflow.list>>,
];

type AllAttachmentPayloadContracts = [
  Assert<PayloadMatchesSdk<typeof attachments.upload, typeof client.drive.media.uploadAll>>,
  Assert<PayloadMatchesSdk<typeof attachments.prepareUpload, typeof client.drive.media.uploadPrepare>>,
  Assert<PayloadMatchesSdk<typeof attachments.uploadPart, typeof client.drive.media.uploadPart>>,
  Assert<PayloadMatchesSdk<typeof attachments.finishUpload, typeof client.drive.media.uploadFinish>>,
  Assert<PayloadMatchesSdk<typeof attachments.download, typeof client.drive.media.download>>,
  Assert<PayloadMatchesSdk<typeof attachments.batchGetTmpDownloadUrl, typeof client.drive.media.batchGetTmpDownloadUrl>>,
];

void (0 as unknown as AllBitablePayloadContracts);
void (0 as unknown as AllAttachmentPayloadContracts);

methods.apps.get({ path: { app_token: "app_token" } });
methods.tables.list({ path: { app_token: "app_token" } });
methods.records.list({
  path: { app_token: "app_token", table_id: "table_id" },
  params: { page_size: 100 },
});
methods.records.create({
  path: { app_token: "app_token", table_id: "table_id" },
  params: {
    user_id_type: "open_id",
    client_token: "00000000-0000-4000-8000-000000000000",
    ignore_consistency_check: false,
  },
  data: { fields: { Title: "example" } },
});

methods.records.list({
  path: { app_token: "app_token", table_id: "table_id" },
  params: {
    // @ts-expect-error page_size must be numeric.
    page_size: "many",
  },
});

// @ts-expect-error app_token must be a string.
methods.apps.get({ path: { app_token: 123 } });

// @ts-expect-error record listing requires both app_token and table_id.
methods.records.list({ path: { app_token: "app_token" } });

async function responseTypesArePreserved(): Promise<void> {
  const response = await methods.records.list({
    path: { app_token: "app_token", table_id: "table_id" },
  });
  const apiCode: number | undefined = response.code;
  void apiCode;
}

void responseTypesArePreserved;

attachments.upload({
  data: {
    file_name: "attachment.txt",
    parent_type: "bitable_file",
    parent_node: "app_token",
    size: 1,
    file: Buffer.from("x"),
  },
});

attachments.upload({
  data: {
    file_name: "attachment.txt",
    // @ts-expect-error Bitable media parent_type must be an official enum value.
    parent_type: "bitable_attachment",
    parent_node: "app_token",
    size: 1,
    file: Buffer.from("x"),
  },
});
