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
type PayloadMatchesSdk<Wrapped, Sdk> = Assert<
  Equal<
    Parameters<Extract<Wrapped, (...args: any[]) => any>>[0],
    NonNullable<Parameters<Extract<Sdk, (...args: any[]) => any>>[0]>
  >
>;

// Every public Bitable wrapper must keep the exact first-argument schema
// from its corresponding official SDK method.
type AllBitablePayloadContracts = [
  PayloadMatchesSdk<typeof methods.apps.create, typeof client.bitable.app.create>,
  PayloadMatchesSdk<typeof methods.apps.get, typeof client.bitable.app.get>,
  PayloadMatchesSdk<typeof methods.apps.update, typeof client.bitable.app.update>,
  PayloadMatchesSdk<typeof methods.apps.copy, typeof client.bitable.app.copy>,
  PayloadMatchesSdk<typeof methods.tables.create, typeof client.bitable.appTable.create>,
  PayloadMatchesSdk<typeof methods.tables.list, typeof client.bitable.appTable.list>,
  PayloadMatchesSdk<typeof methods.tables.update, typeof client.bitable.appTable.patch>,
  PayloadMatchesSdk<typeof methods.tables.delete, typeof client.bitable.appTable.delete>,
  PayloadMatchesSdk<typeof methods.tables.batchCreate, typeof client.bitable.appTable.batchCreate>,
  PayloadMatchesSdk<typeof methods.tables.batchDelete, typeof client.bitable.appTable.batchDelete>,
  PayloadMatchesSdk<typeof methods.records.create, typeof client.bitable.appTableRecord.create>,
  PayloadMatchesSdk<typeof methods.records.get, typeof client.bitable.appTableRecord.get>,
  PayloadMatchesSdk<typeof methods.records.list, typeof client.bitable.appTableRecord.list>,
  PayloadMatchesSdk<typeof methods.records.search, typeof client.bitable.appTableRecord.search>,
  PayloadMatchesSdk<typeof methods.records.update, typeof client.bitable.appTableRecord.update>,
  PayloadMatchesSdk<typeof methods.records.delete, typeof client.bitable.appTableRecord.delete>,
  PayloadMatchesSdk<typeof methods.records.batchCreate, typeof client.bitable.appTableRecord.batchCreate>,
  PayloadMatchesSdk<typeof methods.records.batchGet, typeof client.bitable.appTableRecord.batchGet>,
  PayloadMatchesSdk<typeof methods.records.batchUpdate, typeof client.bitable.appTableRecord.batchUpdate>,
  PayloadMatchesSdk<typeof methods.records.batchDelete, typeof client.bitable.appTableRecord.batchDelete>,
  PayloadMatchesSdk<typeof methods.fields.create, typeof client.bitable.appTableField.create>,
  PayloadMatchesSdk<typeof methods.fields.list, typeof client.bitable.appTableField.list>,
  PayloadMatchesSdk<typeof methods.fields.update, typeof client.bitable.appTableField.update>,
  PayloadMatchesSdk<typeof methods.fields.delete, typeof client.bitable.appTableField.delete>,
  PayloadMatchesSdk<typeof methods.views.create, typeof client.bitable.appTableView.create>,
  PayloadMatchesSdk<typeof methods.views.get, typeof client.bitable.appTableView.get>,
  PayloadMatchesSdk<typeof methods.views.list, typeof client.bitable.appTableView.list>,
  PayloadMatchesSdk<typeof methods.views.update, typeof client.bitable.appTableView.patch>,
  PayloadMatchesSdk<typeof methods.views.delete, typeof client.bitable.appTableView.delete>,
  PayloadMatchesSdk<typeof methods.forms.get, typeof client.bitable.appTableForm.get>,
  PayloadMatchesSdk<typeof methods.forms.update, typeof client.bitable.appTableForm.patch>,
  PayloadMatchesSdk<typeof methods.forms.upgrade, typeof client.bitable.appTableForm.upgrade>,
  PayloadMatchesSdk<typeof methods.forms.listFields, typeof client.bitable.appTableFormField.list>,
  PayloadMatchesSdk<typeof methods.forms.updateField, typeof client.bitable.appTableFormField.patch>,
  PayloadMatchesSdk<typeof methods.fieldGroups.create, typeof client.bitable.appTableFieldGroup.create>,
  PayloadMatchesSdk<typeof methods.dashboards.list, typeof client.bitable.appDashboard.list>,
  PayloadMatchesSdk<typeof methods.dashboards.copy, typeof client.bitable.appDashboard.copy>,
  PayloadMatchesSdk<typeof methods.roles.create, typeof client.bitable.appRole.create>,
  PayloadMatchesSdk<typeof methods.roles.list, typeof client.bitable.appRole.list>,
  PayloadMatchesSdk<typeof methods.roles.update, typeof client.bitable.appRole.update>,
  PayloadMatchesSdk<typeof methods.roles.delete, typeof client.bitable.appRole.delete>,
  PayloadMatchesSdk<typeof methods.roles.listMembers, typeof client.bitable.appRoleMember.list>,
  PayloadMatchesSdk<typeof methods.roles.createMember, typeof client.bitable.appRoleMember.create>,
  PayloadMatchesSdk<typeof methods.roles.batchCreateMembers, typeof client.bitable.appRoleMember.batchCreate>,
  PayloadMatchesSdk<typeof methods.roles.deleteMember, typeof client.bitable.appRoleMember.delete>,
  PayloadMatchesSdk<typeof methods.roles.batchDeleteMembers, typeof client.bitable.appRoleMember.batchDelete>,
  PayloadMatchesSdk<typeof methods.workflows.list, typeof client.bitable.appWorkflow.list>,
  PayloadMatchesSdk<typeof methods.workflows.update, typeof client.bitable.appWorkflow.update>,
  PayloadMatchesSdk<typeof methods.blockWorkflows.list, typeof client.bitable.appBlockWorkflow.list>,
];

type AllAttachmentPayloadContracts = [
  PayloadMatchesSdk<typeof attachments.upload, typeof client.drive.media.uploadAll>,
  PayloadMatchesSdk<typeof attachments.prepareUpload, typeof client.drive.media.uploadPrepare>,
  PayloadMatchesSdk<typeof attachments.uploadPart, typeof client.drive.media.uploadPart>,
  PayloadMatchesSdk<typeof attachments.finishUpload, typeof client.drive.media.uploadFinish>,
  PayloadMatchesSdk<typeof attachments.download, typeof client.drive.media.download>,
  PayloadMatchesSdk<typeof attachments.batchGetTmpDownloadUrl, typeof client.drive.media.batchGetTmpDownloadUrl>,
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
